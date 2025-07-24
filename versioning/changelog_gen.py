import subprocess
import re
from datetime import datetime
from loguru import logger # Import loguru
import sys
import os

def run_command(command_list):
    """Runs a shell command and returns its output."""
    result = subprocess.run(command_list, capture_output=True, text=True, check=True)
    return result.stdout.strip()

def get_latest_tag():
    """Gets the latest Git tag."""
    try:
        return run_command(["git", "describe", "--tags", "--abbrev=0"])
    except subprocess.CalledProcessError:
        logger.info("No Git tags found.")
        return None

def get_current_version(pyproject_path: str):
    """Reads the current version from pyproject.toml."""
    try:
        with open(pyproject_path, "r") as f:
            content = f.read()
            match = re.search(r'current_version = "(.*?)"', content)
            if match:
                return match.group(1)
    except FileNotFoundError:
        logger.error(f"Error: {pyproject_path} not found.")
    except Exception as e:
        logger.error(f"An error occurred while reading {pyproject_path}: {e}")
    return None

def generate_changelog_content(latest_tag, current_version):
    """Generates changelog content using git-changelog."""
    if latest_tag:
        # Generate changelog from latest tag to current HEAD
        command = ["git-changelog", "--output", "-", f"{latest_tag}..HEAD"]
    else:
        # Generate full changelog if no tags exist
        command = ["git-changelog", "--output", "-"]
    
    try:
        return run_command(command)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error generating changelog: {e.stderr}")
        return ""

def update_changelog_file(new_content, current_version):
    """Updates the changelog.md file with new content."""
    changelog_path = "changelog.md"
    today_date = datetime.now().strftime("%Y-%m-%d")
    new_version_heading = f"## [v{current_version}]\n### {today_date}\n" # Added newline

    try:
        with open(changelog_path, "r") as f:
            lines = f.readlines()

        output_lines = []
        unreleased_found = False
        for line in lines:
            output_lines.append(line)
            if "## [Unreleased]" in line:
                unreleased_found = True
                # Insert new content after the Unreleased heading
                output_lines.append(f"\n{new_content}\n")
                output_lines.append(f"{new_version_heading}\n") # Add the new version heading

        if not unreleased_found:
            # If no Unreleased section, add it at the beginning
            output_lines.insert(0, f"## [Unreleased]\n\n{new_content}\n{new_version_heading}\n\n")

        with open(changelog_path, "w") as f:
            f.writelines(output_lines)
        logger.info(f"Updated {changelog_path} with version {current_version} changelog.")

    except FileNotFoundError:
        logger.error(f"Error: {changelog_path} not found.")
    except Exception as e:
        logger.error(f"An error occurred while updating changelog: {e}")

if __name__ == "__main__":
    # Configure Loguru for this script (minimal setup for standalone execution)
    logger.remove() # Remove default handler
    logger.add(sys.stderr, level="INFO", colorize=True,
               format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")

    # Get pyproject.toml path from command line argument
    if len(sys.argv) < 2:
        logger.error("Usage: python changelog_gen.py <path_to_pyproject.toml>")
        sys.exit(1)
    
    pyproject_toml_path = sys.argv[1]

    latest_tag = get_latest_tag()
    current_version = get_current_version(pyproject_toml_path)

    if not current_version:
        logger.error("Could not determine current version. Exiting.")
        sys.exit(1)
    else:
        logger.info(f"Generating changelog for version {current_version} from tag {latest_tag if latest_tag else 'beginning of history'}...")
        changelog_content = generate_changelog_content(latest_tag, current_version)
        if changelog_content:
            update_changelog_file(changelog_content, current_version)
        else:
            logger.info("No changelog content generated.")