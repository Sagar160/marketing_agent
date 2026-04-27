import json
import os
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st
from anthropic import Anthropic
from dotenv import load_dotenv

APP_DIR = Path(__file__).resolve().parent


def load_env_files() -> None:
    candidates = [
        APP_DIR / ".env",
        Path.cwd() / ".env",
    ]
    for env_file in candidates:
        if env_file.exists():
            load_dotenv(dotenv_path=env_file, override=False)


def resolve_prompts_dir() -> Path:
    candidates = [
        APP_DIR / "prompts/media_posts",
        Path.cwd() / "prompts",
    ]
    for path in candidates:
        if (path / "platform_prompts.json").exists() and (path / "system_prompt_template.txt").exists():
            return path
    raise FileNotFoundError("Could not find prompts files in current setup.")


load_env_files()

PROMPTS_DIR = resolve_prompts_dir()
PROMPTS_FILE = PROMPTS_DIR / "platform_prompts.json"
SYSTEM_TEMPLATE_FILE = PROMPTS_DIR / "system_prompt_template.txt"


def load_prompt_library() -> dict[str, dict[str, str]]:
    with PROMPTS_FILE.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    if not isinstance(data, dict) or not data:
        raise ValueError("Prompt library is empty or invalid.")

    for platform, entry in data.items():
        if not isinstance(entry, dict):
            raise ValueError(f"Invalid prompt entry for platform: {platform}")
        if "guide" not in entry or "sample_prompt" not in entry:
            raise ValueError(f"Prompt entry for {platform} must include guide and sample_prompt.")

    return data


def load_system_template() -> str:
    return SYSTEM_TEMPLATE_FILE.read_text(encoding="utf-8")


def build_system_prompt(platform: str, guide: str, user_prompt: str, template: str) -> str:
        return template.format(platform=platform, guide=guide, user_prompt=user_prompt).strip()


def get_client(api_key: str | None) -> Anthropic:
    resolved_key = api_key or os.getenv("ANTHROPIC_API_KEY")
    if not resolved_key:
        raise ValueError("Missing Anthropic API key. Set it in the sidebar or as ANTHROPIC_API_KEY.")
    return Anthropic(api_key=resolved_key)


def extract_json(text: str) -> Any:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:].strip()
    return json.loads(text)


def generate_posts(
    client: Anthropic,
    platform: str,
    guide: str,
    user_prompt: str,
    model: str,
    system_template: str,
) -> list[dict[str, Any]]:
    response = client.messages.create(
        model=model,
        max_tokens=1200,
        temperature=0.7,
        system=build_system_prompt(platform, guide, user_prompt, system_template),
        messages=[
            {
                "role": "user",
                "content": user_prompt,
            }
        ],
    )
    text = "".join(block.text for block in response.content if getattr(block, "type", "") == "text")
    payload = extract_json(text)
    return payload.get("items", [])


def main() -> None:
    try:
        prompt_library = load_prompt_library()
        system_template = load_system_template()
    except Exception as exc:
        st.error(f"Failed to load prompts from prompts folder: {exc}")
        return

    platform_names = list(prompt_library.keys())
    sample_prompts = {name: prompt_library[name]["sample_prompt"] for name in platform_names}

    st.set_page_config(page_title="Social Post Lab", page_icon="✍️", layout="wide")
    st.title("Social Post Lab")
    st.caption("Test prompts for social platforms with Claude and get post ideas in a table.")

    with st.sidebar:
        st.header("Settings")
        api_key = st.text_input("Anthropic API Key", type="password", value=os.getenv("ANTHROPIC_API_KEY", ""))
        model = st.text_input("Claude Model", value=os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514"))
        platforms = st.multiselect(
            "Platforms",
            platform_names,
            default=platform_names[:3],
        )
        st.divider()
        st.subheader("Example prompts")
        selected_example = st.selectbox("Load sample", ["Custom"] + platform_names)
        if selected_example != "Custom":
            st.session_state["prompt_input"] = sample_prompts[selected_example]

    prompt = st.text_area(
        "Your prompt",
        value=st.session_state.get("prompt_input", ""),
        height=180,
        placeholder="Describe the product, offer, audience, and tone you want.",
        key="prompt_input",
    )

    generate = st.button("Generate post table", type="primary")

    if generate:
        if not platforms:
            st.error("Choose at least one platform.")
            return
        if not prompt.strip():
            st.error("Enter a prompt first.")
            return

        try:
            client = get_client(api_key)
        except ValueError as exc:
            st.error(str(exc))
            return

        rows: list[dict[str, Any]] = []
        with st.spinner("Generating posts with Claude..."):
            for platform in platforms:
                try:
                    items = generate_posts(
                        client=client,
                        platform=platform,
                        guide=prompt_library[platform]["guide"],
                        user_prompt=prompt,
                        model=model,
                        system_template=system_template,
                    )
                except Exception as exc:  # pragma: no cover - user-facing app error path
                    st.error(f"{platform}: {exc}")
                    continue

                for item in items:
                    rows.append(
                        {
                            "Platform": platform,
                            "Angle": item.get("angle", ""),
                            "Primary Post": item.get("primary_post", ""),
                            "Alternate Post": item.get("alternate_post", ""),
                            "CTA": item.get("cta", ""),
                            "Hashtags": ", ".join(item.get("hashtags", [])),
                        }
                    )

        if rows:
            df = pd.DataFrame(rows)
            st.success(f"Generated {len(df)} post options.")
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.download_button(
                "Download as CSV",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name="social_posts.csv",
                mime="text/csv",
            )
        else:
            st.warning("No post options were returned.")


if __name__ == "__main__":
    main()
