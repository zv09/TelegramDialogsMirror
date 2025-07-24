import subprocess
import re
import os
from datetime import datetime

def run_command(command):
    result = subprocess.run(command, capture_output=True, text=True, shell=True, check=True)
    return result.stdout.strip()

def get_git_tags():
    tags = run_command("git tag --sort=-v:refname").split('\n')
    return [tag for tag in tags if tag]

def get_commit_log(start_ref, end_ref):
    command = f"git log --pretty=format:'%H%n%s%n%b%n---COMMIT-END---' {start_ref}..{end_ref}"
    return run_command(command)

def parse_commit(commit_str):
    parts = commit_str.split('\n---COMMIT-END---')
    parsed_commits = []
    for part in parts:
        if not part.strip():
            continue
        lines = part.strip().split('\n')
        if len(lines) < 2:
            continue
        
        commit_hash = lines[0]
        subject = lines[1]
        body = '\n'.join(lines[2:]).strip()

        type_scope_desc = re.match(r'^(feat|fix|build|chore|ci|docs|perf|refactor|revert|style|test)(\((.+)\))?:\s*(.*)$', subject)
        
        commit_type = 'misc'
        commit_scope = None
        description = subject
        is_breaking_change = False

        if type_scope_desc:
            commit_type = type_scope_desc.group(1)
            commit_scope = type_scope_desc.group(3)
            description = type_scope_desc.group(4)
        
        if "BREAKING CHANGE:" in body or "BREAKING-CHANGE:" in body:
            is_breaking_change = True

        parsed_commits.append({
            'hash': commit_hash,
            'type': commit_type,
            'scope': commit_scope,
            'description': description,
            'body': body,
            'is_breaking_change': is_breaking_change
        })
    return parsed_commits

def generate_changelog_content():
    tags = get_git_tags()
    changelog_sections = {}
    
    # Handle Unreleased section
    unreleased_commits_log = get_commit_log(tags[0] if tags else 'HEAD', 'HEAD')
    unreleased_commits = parse_commit(unreleased_commits_log)
    changelog_sections['Unreleased'] = unreleased_commits

    # Handle tagged releases
    for i in range(len(tags)):
        tag = tags[i]
        prev_tag = tags[i+1] if i + 1 < len(tags) else ''
        
        commits_log = get_commit_log(prev_tag, tag)
        commits = parse_commit(commits_log)
        changelog_sections[tag] = commits
    
    output = "# Changelog\n\nAll notable changes to this project will be documented in this file.\n\n"

    # Sort sections to ensure Unreleased is first, then by version (desc)
    def version_key(version_string):
        # Remove 'v' prefix if present and split by '.'
        parts = re.findall(r'\d+', version_string)
        return [int(p) for p in parts]

    sorted_versions = sorted([v for v in changelog_sections.keys() if v != 'Unreleased'], key=version_key, reverse=True)
    ordered_sections = ['Unreleased'] + sorted_versions

    for version in ordered_sections:
        commits = changelog_sections[version]
        if not commits:
            continue

        output += f"## [{version}]\n"
        if version != 'Unreleased':
            # Get tag date
            try:
                tag_date_str = run_command(f"git log -1 --format=%ai {version}").split(' ')[0]
                output += f"### {tag_date_str}\n"
            except:
                pass # If tag date can't be fetched, skip it

        features = [c for c in commits if c['type'] == 'feat']
        fixes = [c for c in commits if c['type'] == 'fix']
        breaking_changes = [c for c in commits if c['is_breaking_change']]
        refactors = [c for c in commits if c['type'] == 'refactor']
        docs = [c for c in commits if c['type'] == 'docs']
        misc = [c for c in commits if c['type'] not in ['feat', 'fix', 'refactor', 'docs']]

        if breaking_changes:
            output += "\n### Breaking Changes\n"
            for commit in breaking_changes:
                output += f"- **{commit['scope']}:** {commit['description']} (_{commit['hash'][:7]}_)\n"
        
        if features:
            output += "\n### Features\n"
            for commit in features:
                scope_prefix = f"**{commit['scope']}:** " if commit['scope'] else ""
                output += f"- {scope_prefix}{commit['description']} (_{commit['hash'][:7]}_)\n"

        if fixes:
            output += "\n### Bug Fixes\n"
            for commit in fixes:
                scope_prefix = f"**{commit['scope']}:** " if commit['scope'] else ""
                output += f"- {scope_prefix}{commit['description']} (_{commit['hash'][:7]}_)\n"

        if refactors:
            output += "\n### Refactor\n"
            for commit in refactors:
                scope_prefix = f"**{commit['scope']}:** " if commit['scope'] else ""
                output += f"- {scope_prefix}{commit['description']} (_{commit['hash'][:7]}_)\n"

        if docs:
            output += "\n### Documentation\n"
            for commit in docs:
                scope_prefix = f"**{commit['scope']}:** " if commit['scope'] else ""
                output += f"- {scope_prefix}{commit['description']} (_{commit['hash'][:7]}_)\n"

        if misc:
            output += "\n### Miscellaneous\n"
            for commit in misc:
                scope_prefix = f"**{commit['scope']}:** " if commit['scope'] else ""
                output += f"- {commit['type']}{f"({commit['scope']})" if commit['scope'] else ''}: {scope_prefix}{commit['description']} (_{commit['hash'][:7]}_)\n"
        
        output += "\n" # Add a newline for separation between versions

    return output

if __name__ == "__main__":
    changelog_content = generate_changelog_content()
    with open("changelog.md", "w") as f:
        f.write(changelog_content)
    print("Changelog generated successfully to changelog.md")
