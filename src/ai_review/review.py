import os
import sys
import requests
import anthropic

def get_pr_diff(repo, pr_number, token):
    """Fetches the raw diff of the Pull Request from GitHub API."""
    url = f"https://github.com/{repo}/pulls/{pr_number}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3.diff",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching PR diff: {response.status_code} - {response.text}")
        sys.exit(1)
        
    return response.text

def review_diff(diff_text):
    """Sends the diff text to Claude for analysis and returns the markdown review."""
    # The client automatically picks up ANTHROPIC_API_KEY from the environment variables
    client = anthropic.Anthropic()
    
    system_prompt = (
        "You are an expert senior software engineer conducting a code review.\n"
        "Analyze the provided git diff and generate a concise, professional markdown review.\n"
        "Your review MUST include:\n"
        "1. 🎯 Summary of changes (what changed and why)\n"
        "2. ⚠️ Potential Risks or bugs (security flaws, performance issues, logic gaps)\n"
        "3. 💡 Actionable suggestions for improvement\n\n"
        "Be constructive, polite, and clear. Avoid nitpicking minor formatting unless critical."
    )
    
    try:
        # Using the standard modern Claude 3.5 Sonnet model
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=2000,
            system=system_prompt,
            messages=[
                {"role": "user", "content": f"Please review this PR diff:\n\n{diff_text}"}
            ]
        )
        return message.content[0].text
    except Exception as e:
        print(f"Error communicating with Claude API: {e}")
        sys.exit(1)

def post_comment(repo, pr_number, token, body_text):
    """Posts the final Claude review as a comment on the PR."""
    url = f"https://github.com/{repo}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    payload = {"body": body_text}
    
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 201:
        print(f"Error posting comment to PR: {response.status_code} - {response.text}")
        sys.exit(1)
    print("Successfully posted Claude's review to the PR!")

if __name__ == "__main__":
    # Pull required values securely from environment variables mapped by GitHub Actions
    repo = os.getenv("REPO")
    pr_number = os.getenv("PR_NUMBER")
    github_token = os.getenv("GITHUB_TOKEN")
    
    if not all([repo, pr_number, github_token]):
        print("Missing required environment variables (REPO, PR_NUMBER, or GITHUB_TOKEN).")
        sys.exit(1)
        
    print(f"Starting Claude PR Review for {repo} PR #{pr_number}...")
    
    diff = get_pr_diff(repo, pr_number, github_token)
    
    if not diff.strip():
        print("PR diff is empty. Skipping review.")
        sys.exit(0)
        
    review = review_diff(diff)
    post_comment(repo, pr_number, github_token, review)
