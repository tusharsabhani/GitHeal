# AGENTS.md

Instructions for AI Agents working in this Workspace.

## Setup Requirements
This is a `uv` project. To set up:
1. Ensure `uv` is installed on your local path.
2. Initialize virtual environment:
   ```bash
   uv venv
   ```
3. Install dependencies:
   ```bash
   uv pip install -e .
   ```

## Development and Orchestration
- **Mock Server**: Start using `uv run uvicorn tools.mock_server:app --reload --port 8000` to mock the remote endpoint locally.
- **Client Script**: Run `uv run tools/api_fetcher.py` to check the schema.
- **Self-Healing Loop**:
  - The script `tools/api_fetcher.py` parses upstream payloads and maps them using `normalize_payload`.
  - When validation fails, the agent must update the `normalize_payload` code in `tools/api_fetcher.py`.
  - Execute `tools/gitclaw_hooks.py` to commit modifications and write the PR description to `pr_payload.json`.

## Code Standard
- Maintain complete type annotations.
- Keep dependency files up to date using `pyproject.toml`.
- Do not add packages uploaded to PyPI within the last 30 days.
