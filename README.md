# Gitlab User Audit

This script will print out a list of users that have access to a Projects under a top level group.

Requirements:
- Gitlab API Key/Personal Access Token. This can be set via `GITLAB_API_KEY` environment variable or you will be prompted for it.
- top level group ID. This can be set via `GITLAB_GROUP_ID` environment variable or you will be prompted for it.

Usage:
```bash
    $ python3 -m venv .venv
    $ source .venv/bin/activate
    $ pip install -r requirements.txt
    $ GITLAB_API_KEY=<your_api_key> GITLAB_GROUP_ID=<your_group_id> python3 audit.py
```

This will create or overwrite a file called "audit.xlsx" in the current directory with a list of users, what projects and groups they are assigned to.