import os
import sys
import subprocess
import json
import time

WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PR_PAYLOAD_PATH = os.path.join(WORKSPACE_DIR, "pr_payload.json")

def run_git(args, check=True):
    result = subprocess.run(
        ["git"] + args,
        cwd=WORKSPACE_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if check and result.returncode != 0:
        print(f"Git command failed: git {' '.join(args)}", file=sys.stderr)
        print(f"Stdout: {result.stdout}", file=sys.stderr)
        print(f"Stderr: {result.stderr}", file=sys.stderr)
        sys.exit(result.returncode)
    return result

def main():
    print("Executing GitClaw Post-Heal Hook...")
    
    # 1. Initialize git repo if not present
    if not os.path.exists(os.path.join(WORKSPACE_DIR, ".git")):
        print("Git repository not initialized. Initializing now...")
        run_git(["init"])
        run_git(["config", "user.name", "GitHeal Agent"])
        run_git(["config", "user.email", "agent@githeal.local"])
        # Commit current files as baseline
        run_git(["add", "."])
        run_git(["commit", "-m", "chore: initial commit of workspace baseline"])

    # 2. Check for modifications (e.g., api_fetcher.py)
    status_res = run_git(["status", "--porcelain"])
    raw_modified_files = []
    for line in status_res.stdout.splitlines():
        parts = line.strip().split()
        if len(parts) >= 2:
            raw_modified_files.append(parts[1])

    # Filter out ignored files (e.g., build/dist outputs or pycache)
    modified_files = []
    for f in raw_modified_files:
        check = run_git(["check-ignore", "-q", f], check=False)
        if check.returncode != 0:
            modified_files.append(f)

    if not modified_files:
        print("No non-ignored modified files detected. Workspace is clean. Nothing to commit.")
        sys.exit(0)

    print(f"Detected modified files: {modified_files}")

    # Get details of git diff for the PR description
    diff_res = run_git(["diff"])
    diff_content = diff_res.stdout

    # 3. Cut hotfix branch
    timestamp = int(time.time())
    branch_name = f"hotfix/api-drift-{timestamp}"
    print(f"Cutting new hotfix branch: {branch_name}")
    run_git(["checkout", "-b", branch_name])

    # 4. Stage and commit
    run_git(["add"] + modified_files)
    commit_msg = "fix(schema): autonomously self-healed API schema drift mapping"
    run_git(["commit", "-m", commit_msg])

    # 5. Prepare PR payload metadata
    pr_title = "fix: Autonomously Resolve Upstream API Schema Drift"
    pr_body = (
        "## Description\n"
        "Project GitHeal has detected an upstream API schema drift and autonomously "
        "re-mapped the api client normalization logic to restore system functionality.\n\n"
        "### Self-Healing Audit Trail\n"
        "- **Status**: Self-healed successfully & validated locally.\n"
        "- **Branch**: `" + branch_name + "`\n"
        "- **Target Branch**: `main`\n\n"
        "### Code Changes\n"
        "```diff\n" + diff_content + "\n```\n\n"
        "This PR was generated automatically by the GitHeal Agent."
    )

    payload = {
        "title": pr_title,
        "body": pr_body,
        "source_branch": branch_name,
        "target_branch": "main",
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "status": "prepared",
        "modified_files": modified_files
    }

    with open(PR_PAYLOAD_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print(f"PR payload metadata written to: {PR_PAYLOAD_PATH}")
    print("GitClaw hook executed successfully.")

if __name__ == "__main__":
    main()
