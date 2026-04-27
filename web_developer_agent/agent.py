import json
import os
from pathlib import Path
from typing import Annotated, List

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langgraph.graph import END, StateGraph
from pydantic import BaseModel, Field


ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=ROOT_DIR / ".env", override=False)


class WebPlan(BaseModel):
    files: List[str] = Field(
        description="List of website files to create (for example: ['index.html', 'style.css', 'script.js'])"
    )
    files_reasoning: List[str] = Field(description="Reasoning about why these files are needed for the website")
    shared_design: str = Field(description="Shared design decisions that should be reflected across all files, for example color scheme, fonts, layout style, class names, etc.")
 
class SavedFile(BaseModel):
    filename: str = Field(description="Generated filename")
    content: str = Field(description="Full file code")

class AgentState(BaseModel):
    messages: Annotated[List[BaseMessage], lambda x, y: x + y] = Field(default_factory=list)
    plan: WebPlan | None = None
    completed_files: Annotated[List[str], lambda x, y: x + y] = Field(default_factory=list)
    current_task: str = ""
    iteration: int = 0
    code: List[str] = Field(description="List of codes", default_factory=list)
    current_filename: str = ""
    saved_files: Annotated[List[SavedFile], lambda x, y: x + y] = Field(default_factory=list)


class DeveloperOutput(BaseModel):
    filename: str = Field(description="Target file name")
    content: str = Field(description="Complete file content")


def parse_developer_output(text: str) -> DeveloperOutput:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.startswith("json"):
            cleaned = cleaned[4:].strip()

    payload = json.loads(cleaned)
    return DeveloperOutput(**payload)


def llm_init() -> ChatAnthropic:
    # model_name = os.getenv("ANTHROPIC_MODEL") or os.getenv("CLAUDE_MODEL") or "claude-sonnet-4-20250514"
    # if model_name in {"claude-2", "claude-1", "claude-instant-1", "claude-instant-1.2"}:
    #     model_name = "claude-sonnet-4-20250514"
    # use cheap model Haiku
    model_name = 'claude-haiku-4-5-20251001'
    return ChatAnthropic(model=model_name, temperature=0.7, max_tokens=8500)


def planner(state: AgentState):
    model = llm_init()
    planner_llm = model.with_structured_output(WebPlan)
    plan = planner_llm.invoke(state.messages)

    plan_message = 'Here is the plan for the website:\n'
    for file in plan.files:
        plan_message += f"- {file}\n"
        plan_message += f"  Reasoning: {plan.files_reasoning[plan.files.index(file)]}\n"

    plan_message += f"- Shared design decisions: {plan.shared_design}"
    return {
        "plan": plan,
        "messages": [AIMessage(content=plan_message)],
    }

def manager(state: AgentState):
    "Let break down the plan into tasks and execute them iteratively"
    if not state.plan:
        return {"messages": [AIMessage(content="No plan found. Please create a plan first.")]}
    
    # use developer to create the content for the first file in the plan that has not been completed yet
    for file in state.plan.files:
        if file not in state.completed_files:
            return {
                "current_task": file,
                "messages": [AIMessage(content=f"Assigning task: Create {file}")]
            }
        
    return {
        "current_task": "DONE",
        "messages": [AIMessage(content="All planned files are completed.")],
    }

    
def developer(state: AgentState):
    "This agent will take the current task and create the corresponding file content"
    file_to_create = state.current_task
    if not state.plan or file_to_create == "DONE":
        return {"messages": [AIMessage(content="No developer task to execute.")]}

    file_reasoning = state.plan.files_reasoning[state.plan.files.index(file_to_create)]

    prompt = f"""You are a web developer.
Create the complete code for file: {file_to_create}\n
Reasoning: {file_reasoning}\n
shared design decisions to reflect in the code: {state.plan.shared_design}

Return valid JSON only with this exact shape:
{{"filename": "{file_to_create}", "content": "<full file code>"}}

Do not include markdown or explanations.
"""

    model = llm_init()
    try:
        raw = model.invoke(prompt)
        parsed = parse_developer_output(raw.content)
    except Exception as exc:
        retry_prompt = (
            f"{prompt}\n"
            f"Previous output was invalid. Return only valid JSON with both filename and content. Error: {exc}"
        )
        raw = model.invoke(retry_prompt)
        parsed = parse_developer_output(raw.content)

    if not parsed.content.strip():
        raise ValueError("Developer returned empty content.")

    return {
        "code": [parsed.content],
        "current_filename": file_to_create,
        "completed_files": [file_to_create],
        "saved_files": [SavedFile(filename=file_to_create, content=parsed.content)],
        "messages": [AIMessage(content=f"Created content for {file_to_create}")],
    }

def save_files(state: AgentState):
    for file in state.saved_files:
        file_path = ROOT_DIR / "output" / file.filename
        file_path.parent.mkdir(exist_ok=True)
        with open(file_path, "w") as f:
            f.write(file.content)
    return {"messages": [AIMessage(content=f"Saved {len(state.saved_files)} files to disk.")]}


def manager_router(state: AgentState):
    if state.current_task == "DONE":
        return "SAVE_FILES"
    return "developer"


    
workflow = StateGraph(AgentState)
workflow.add_node("planner", planner)
workflow.add_node("manager", manager)
workflow.add_node("developer", developer)
workflow.add_node("save_files", save_files)

workflow.set_entry_point("planner")
workflow.add_edge("planner", "manager")
workflow.add_conditional_edges(
    "manager",
    manager_router,
    {
        "developer": "developer",
        "SAVE_FILES": "save_files",
    },
)
workflow.add_edge("developer", "manager")
workflow.add_edge("save_files", END)

app = workflow.compile()
graph = app


if __name__ == "__main__":
    input_data = {
        "messages": [
            HumanMessage(content="Create a responsive portfolio website with navbar, hero, projects and contact form.")
        ]
    }

    final_state = None
    for chunk in app.stream(input_data, stream_mode="values"):
        final_state = chunk
        if chunk.get("messages"):
            msg = chunk["messages"][-1]
            print(f"\n--- {msg.type} ---")
            print(msg.content)

    if final_state:
        print("\nSaved files in state:")
        for item in final_state.get("saved_files", []):
            print(f"- {item.filename} ({len(item.content)} chars)")