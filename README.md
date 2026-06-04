# Central CI Templates — Claude PR Reviewer

This repository houses a reusable GitHub Actions workflow template that automates code reviews using Anthropic's Claude 3.5 Sonnet. When implemented, it automatically fetches Pull Request diffs, transmits them securely to the Claude API, and publishes an engineering summary directly onto the PR timeline.

## 📁 Repository Structure

```text
central-actions/
├── .github/
│   └── workflows/
│       └── claude-pr-review-template.yml  # The Reusable Workflow Entrypoint
└── src/
    └── ai_review/
        ├── requirements.txt                # Python Dependencies
        └── review.py                       # Core Python Review Script
```

---

## 🛠️ How It Works Under the Hood

1. **Trigger**: An application repository opens or synchronizes a Pull Request.
2. **Double Checkout**: The runner loads the application codebase context, then loads this central script repository into a workspace subfolder (`.central-actions/`).
3. **Diff Extraction**: The workflow extracts the code changes using the native GitHub CLI (`gh pr diff`).
4. **AI Generation**: The script passes the changes to `claude-3-5-sonnet-latest` along with a senior engineering persona.
5. **Timeline Sync**: The feedback is converted to Markdown and written directly to the target Pull Request timeline.

---

## 🚀 Setup & Integration Guide

Follow these simple steps to integrate this automated AI code review process into any external repository.

### Step 1: Add your Anthropic API Key
You must securely store your Anthropic credentials inside the target application repository.

1. Navigate to your target application repository on GitHub.
2. Click **Settings** ➔ **Secrets and variables** ➔ **Actions**.
3. Click the **New repository secret** button.
4. Set the name to exactly: `ANTHROPIC_API_KEY`
5. Paste your Anthropic API credential string (`sk-ant-...`) into the value field and save.

### Step 2: Create the Calling Workflow File
Create a new workflow file in your target application repository at the following path: `.github/workflows/run-review.yml`. 

Paste the snippet below into that file:

```yaml
name: Trigger Claude PR Review

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  call-claude-review:
    # ⚠️ CRITICAL: Must have write permissions to post comments to the PR timeline
    permissions:
      pull-requests: write
      contents: read

    # Reference this public template repository
    uses: imsandeepreddy/central-actions/.github/workflows/claude-pr-review-template.yml@main
    
    secrets:
      ANTHROPIC_API_KEY: \${{ secrets.ANTHROPIC_API_KEY }}
      TARGET_GITHUB_TOKEN: \${{ secrets.GITHUB_TOKEN }} # Automatically handled by GitHub Actions
```

### Step 3: Test the Integration
To test the workflow loop, create a new branch in your application repository, modify a file, and **open a Pull Request**. The workflow will start running, evaluate the diff, and post Claude's markdown feedback on your PR timeline within seconds.

---

## 🛡️ Core Technologies Used
* **GitHub Actions** (`workflow_call` architecture)
* **GitHub CLI** (`gh`) for stable data streaming
* **Anthropic Python SDK** (`claude-3-5-sonnet-latest`)
* **Python 3.11** runtime environment
