# RULES of GitHeal Execution

Strict boundaries and local testing requirements.

## 1. Sandbox and Network Rules
- **Permitted Network Space**: Only local network connections to localhost ports (e.g. `127.0.0.1:8000` for `mock_server`) are allowed.
- **No External Writes**: The agent must not write to any directory outside of the workspace path `c:/Users/tsabh/Desktop/Projects/GitHeal/`.

## 2. Dependency Execution Rules
- **UV Usage**: All execution of python code, scripts, or testing must run via `uv`. Never run naked `python` or `pip` commands.
- **Dependency Cooldown**: The `exclude-newer` parameter inside `pyproject.toml` is set to `"30 days"`. Do not bypass this rule.

## 3. Git Operations Rules
- **Branch Naming**: Branch name must follow the template: `hotfix/api-drift-[timestamp]`.
- **Validation Check**: Never run `git commit` unless `uv run tools/api_fetcher.py --validate` has exited with code `0`.
- **PR Output**: Upon successful patch validation, write the PR metadata structure to `pr_payload.json` in the root workspace.

## 4. Verification Workflow
1. Start mock server using `uv run uvicorn tools.mock_server:app --port 8000`.
2. Toggle server state to healthy or drifted.
3. Validate API response.
4. Auto-remediate if drifted.
5. Cut branch and stage PR metadata.
