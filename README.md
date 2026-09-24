# IaC MCP Server

MCP server that exposes the approved Terraform modules to an AI agent.

## Goal

The model should not invent infrastructure patterns. It should discover a module, inspect its required inputs, validate user values, and generate a Terraform configuration that can be reviewed through GitHub.

## Tools

- `list_modules`
- `get_module`
- `validate_parameters`
- `generate_terraform`

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python server.py
```

The first version uses stdio MCP transport so it can run locally with an Ollama-based agent.
