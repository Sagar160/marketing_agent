# Website Development Agent

This project is a LangGraph-based website development agent.

It plans website files, generates full code per file, keeps generated artifacts in graph state, and writes files to the `output/` directory.

## What It Does

- Creates a file plan for a requested website (for example: `index.html`, `style.css`, `script.js`)
- Tracks file-level reasoning and shared design decisions
- Generates complete code for each planned file
- Stores generated filename and content in state (`saved_files`)
- Saves all generated files to `output/`

## Project Structure

- `web_developer_agent/agent.py`: LangGraph workflow (`graph` export)
- `langgraph.json`: Graph and environment config
- `.env`: API keys and model settings
- `output/`: Generated website files

## Prerequisites

- Python 3.13+
- Anthropic API key

## Setup

1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -e .
```

3. Configure environment variables in `.env`:

```bash
ANTHROPIC_API_KEY=your_key_here
# Optional override
# CLAUDE_MODEL=claude-sonnet-4-20250514
```

## Run The Agent

Option 1: Run directly with Python

```bash
python web_developer_agent/agent.py
```

Option 2: Run with LangGraph CLI

```bash
langgraph dev
```

`langgraph.json` maps the graph entrypoint to:

`web_developer_agent/agent.py:graph`

## Output

Generated files are written to:

`output/`

Each file is produced by the developer node and saved in the final save step.

## Notes

- If a model response is malformed, the developer step retries with stricter JSON instructions.
- If GitHub blocks direct push to `main`, push a feature branch and open a pull request.
