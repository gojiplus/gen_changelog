import git
import os
from markdown import markdown
from datetime import datetime

# Initialize the repo
repo_path = os.getcwd()
repo = git.Repo(repo_path)

# Function to filter major commits
def is_major_change(commit):
    keywords = ["feat", "fix", "breaking", "major"]
    return any(keyword in commit.message.lower() for keyword in keywords)

# Generate the changelog
def generate_changelog():
    changelog = []
    for commit in repo.iter_commits():
        if is_major_change(commit):
            changelog.append({
                "hash": commit.hexsha[:7],
                "message": commit.message.strip(),
                "date": datetime.fromtimestamp(commit.committed_date).strftime('%Y-%m-%d'),
                "files": [diff.a_path for diff in commit.stats.files.keys()]
            })
    return changelog

# Write to markdown
def write_changelog_to_markdown(changelog, output_file="changelog.md"):
    with open(output_file, "w") as f:
        f.write("# Changelog\n\n")
        for entry in changelog:
            f.write(f"## {entry['date']} - {entry['hash']}\n")
            f.write(f"**Message:** {entry['message']}\n\n")
            if entry['files']:
                f.write("**Files Affected:**\n")
                f.write("\n".join(f"- {file}" for file in entry['files']))
            f.write("\n\n")

if __name__ == "__main__":
    changelog = generate_changelog()
    write_changelog_to_markdown(changelog)
    print("Changelog generated as 'changelog.md'")
