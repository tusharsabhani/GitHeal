# Project GitHeal

Project GitHeal is an autonomous API schema self-healing workflow. It prevents production downtime by detecting upstream API changes, patching its own data-mapping functions, and cutting a Git hotfix branch with a prepared GitHub Pull Request.

---

## What This Repository Contains
1. **`knowledge/api_spec.json`**: The baseline JSON Schema representing the API payload structure your app expects.
2. **`tools/api_fetcher.py`**: The validation client that fetches the API data, checks it against the schema, and programmatically self-heals by rewriting its own parser when schema drift occurs.
3. **`tools/mock_server.py`**: A simulator to toggle between a healthy API payload and a drifted payload for testing.
4. **`tools/gitclaw_hooks.py`**: A git helper script that creates a local hotfix branch, commits the self-healed code, and writes a PR metadata file (`pr_payload.json`).
5. **GitAgent manifests**: `agent.yaml`, `SOUL.md`, `RULES.md`, and `AGENTS.md` specifying rules and instructions for Git-native agents.

---

## How to Integrate GitHeal into an Existing Project

Follow these steps to integrate GitHeal into your own service:

### Step 1: Copy the Files
Copy the following files and folders to your target repository:
- `knowledge/api_spec.json`
- `tools/api_fetcher.py`
- `tools/gitclaw_hooks.py`

### Step 2: Configure the API Endpoint
Open `tools/api_fetcher.py` and update the `API_URL` to point to your real API:
```python
API_URL = "https://api.yourdomain.com/endpoint"
```

### Step 3: Define Your Expected Schema
Update `knowledge/api_spec.json` with the JSON Schema your application requires. For example, if you expect a user profile:
```json
{
  "type": "object",
  "properties": {
    "user_id": { "type": "string" },
    "full_name": { "type": "string" },
    "account_status": { "type": "string" }
  },
  "required": ["user_id", "full_name", "account_status"]
}
```

### Step 4: Configure Field Mappings
In `tools/api_fetcher.py`, locate the `potential_mappings` dictionary. Update this list with potential synonyms or old names for each field so the self-healer knows how to resolve changes:
```python
potential_mappings = {
    "full_name": ["display_name", "name", "full_name"],
    "account_status": ["account_state", "status", "account_status"]
}
```

### Step 5: Automate with GitHub Actions
Create a file at `.github/workflows/githeal.yml` in your repository and copy the workflow configuration. We have already created a fully functional file in this repository at [.github/workflows/githeal.yml](file:///c:/Users/tsabh/Desktop/Projects/GitHeal/.github/workflows/githeal.yml) which:
1. Runs once a day or on-demand.
2. Checks out code and installs dependencies using `uv`.
3. Runs the validator with `--heal` to auto-remediate schema drift.
4. Executes the gitclaw hooks if healing was applied (exit code `2`).
5. Pushes the hotfix branch and opens a Pull Request automatically using the GitHub CLI.

To use this, make sure your GitHub repository has write permissions enabled for GitHub Actions (`Settings > Actions > General > Workflow permissions > Read and write permissions`).
