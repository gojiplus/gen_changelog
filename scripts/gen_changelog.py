import git
import os
import openai
import logging
from datetime import datetime
from tqdm import tqdm

# Configure OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("OpenAI API key is not set. Please configure the 'OPENAI_API_KEY' environment variable.")

# Initialize repository
repo_path = os.getcwd()
repo = git.Repo(repo_path)

# Configure logging
logging.basicConfig(filename='changelog_errors.log', level=logging.ERROR)

def summarize_commit(commit, max_tokens=300):
    """
    Generate a summary of a commit using OpenAI.
    """
    commit_message = commit.message.strip()
    diff = "\n".join(
        diff.diff.decode("utf-8", errors="ignore")
        for diff in commit.diff(None, create_patch=True)
    )

    prompt = f"""
    You are an AI assistant creating a human-readable changelog.
    Analyze the following commit details:

    Commit Message:
    {commit_message}

    Code Changes:
    {diff[:3000]}  # Truncate large diffs for efficiency

    Provide a concise summary of the significant changes in plain language.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Summarize code changes for changelogs."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        logging.error(f"Error summarizing commit {commit.hexsha[:7]}: {e}")
        return "Summary unavailable."

def generate_changelog(max_commits=50):
    """
    Generate a changelog with OpenAI-generated summaries.
    """
    changelog = []
    for commit in tqdm(repo.iter_commits(max_count=max_commits), desc="Processing commits"):
        summary = summarize_commit(commit)
        changelog.append({
            "hash": commit.hexsha[:7],
            "message": commit.message.strip(),
            "date": datetime.fromtimestamp(commit.committed_date).strftime('%Y-%m-%d'),
            "summary": summary,
        })
    return changelog

def write_changelog_to_markdown(changelog, output_file="changelog.md"):
    """
    Write the changelog to a markdown file.
    """
    with open(output_file, "w") as f:
        f.write("# Changelog\n\n")
        current_date = None
        for entry in changelog:
            if entry['date'] != current_date:
                current_date = entry['date']
                f.write(f"## {current_date}\n\n")
            f.write(f"### {entry['hash']}\n")
            f.write(f"**Commit Message:** {entry['message']}\n\n")
            f.write(f"**AI Summary:** {entry['summary']}\n\n")

if __name__ == "__main__":
    print("Generating AI-powered changelog...")
    changelog = generate_changelog()
    write_changelog_to_markdown(changelog)
    print("Changelog generated and saved to 'changelog.md'")
