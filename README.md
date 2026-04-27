# Social Post Lab

A small Streamlit app for testing WhatsApp, Instagram, and Facebook post prompts with Claude.

## Setup

1. Activate your virtual environment:

```bash
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set your Anthropic API key:

```bash
export ANTHROPIC_API_KEY="your_key_here"
```

Optional:

```bash
export CLAUDE_MODEL="claude-sonnet-4-20250514"
```

## Run the website

```bash
streamlit run app.py
```

Then open the local URL shown in the terminal, usually:

```bash
http://localhost:8501
```

## What it does

- Lets you paste a prompt for social media copy
- Lets you pick WhatsApp, Instagram, or Facebook
- Calls Claude for each selected platform
- Shows a table of post ideas
- Lets you download the results as CSV
