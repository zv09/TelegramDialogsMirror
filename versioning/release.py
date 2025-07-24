import subprocess
import sys
import os
import re # Import re for regex
from datetime import datetime
from loguru import logger # Import loguru

class ReleaseError(Exception):
    """Custom exception for release process failures."""
    pass

class ReleaseManager:
    def __init__(self, version_part: str, dry_run: bool = False, verbose: bool = False):
        self.version_part = version_part
        self.dry_run = dry_run
        self.verbose = verbose # New verbose flag
        self.original_cwd = os.getcwd()
        self.script_dir = os.path.dirname(os.path.abspath(__file__))

    def _run_command(self, command: str, check_error: bool = True, capture_output: bool = False, cwd: str = None) -> str:
        """
        Runs a shell command and handles errors.
        Returns stdout if capture_output is True, otherwise None.
        Raises ReleaseError on command failure.
        """
        full_command = command if isinstance(command, str) else ' '.join(command)
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would execute: {full_command}")
            return "" # Return empty string for dry run capture_output
        
        logger.debug(f"Executing: {full_command}") # Changed to debug level
        try:
            result = subprocess.run(
                full_command,
                shell=True,
                check=check_error,
                text=True,
                capture_output=True, # Always capture output for detailed logging
                cwd=cwd if cwd else self.original_cwd # Use provided cwd or default to original_cwd
            )
            if result.stdout:
                logger.debug(f"Stdout: {result.stdout.strip()}")
            if result.stderr:
                logger.warning(f"Stderr: {result.stderr.strip()}")
            
            if capture_output:
                return result.stdout.strip()
            return None
        except subprocess.CalledProcessError as e:
            error_message = f"Command failed with exit code {e.returncode}: {e.cmd}\n"
            if e.stdout:
                error_message += f"Stdout: {e.stdout.strip()}\n"
            if e.stderr:
                error_message += f"Stderr: {e.stderr.strip()}\n"
            logger.error(error_message)
            raise ReleaseError(error_message)
        except FileNotFoundError:
            error_message = f"Command not found: {full_command.split(' ')[0]}. Is it installed and in your PATH?"
            logger.error(error_message)
            raise ReleaseError(error_message)
        except Exception as e:
            error_message = f"An unexpected error occurred while running command '{full_command}': {e}"
            logger.exception(error_message) # Logs exception traceback
            raise ReleaseError(error_message)

    def _get_version_from_pyproject(self) -> str:
        """Reads the current version from pyproject.toml."""
        pyproject_path = os.path.join(self.original_cwd, "pyproject.toml")
        try:
            with open(pyproject_path, "r") as f:
                content = f.read()
                match = re.search(r'current_version = "(.*?)"', content)
                if match:
                    return match.group(1)
        except FileNotFoundError:
            raise ReleaseError(f"Error: {pyproject_path} not found.")
        except Exception as e:
            raise ReleaseError(f"An error occurred while reading {pyproject_path}: {e}")
        return "" # Should not be reached

    def _check_clean_working_directory(self):
        """Checks if the Git working directory is clean."""
        logger.info("--- Checking for clean working directory ---")
        status_output = self._run_command("git status --porcelain", capture_output=True)
        if status_output:
            raise ReleaseError(
                "Working directory is not clean. Please commit or stash your changes before running the release script."
            )
        logger.info("Working directory is clean.")

    def _bump_version(self):
        """Runs bump-my-version."""
        logger.info("\n--- Bumping version ---")
        # Pass --dry-run to bump-my-version if our script is in dry_run mode
        dry_run_flag = "--dry-run" if self.dry_run else ""
        
        current_version_before_bump = self._get_version_from_pyproject() # Get version directly
        
        bump_output = self._run_command(f"bump-my-version bump {self.version_part} {dry_run_flag}", capture_output=True)
        logger.debug(f"Bump-my-version output:\n{bump_output}")

        # Get new version after bump (if not dry run)
        if not self.dry_run:
            new_version_after_bump = self._get_version_from_pyproject() # Get version directly
            logger.info(f"Version bumped from {current_version_before_bump} to {new_version_after_bump}.")
        else:
            logger.info(f"[DRY RUN] Version would be bumped from {current_version_before_bump} to a new version.")


    def _generate_changelog(self):
        """Generates changelog using changelog_gen.py."""
        logger.info("\n--- Generating changelog ---")
        pyproject_toml_path = os.path.join(self.original_cwd, "pyproject.toml")
        
        # Read changelog.md before generation
        changelog_before = ""
        try:
            with open("changelog.md", "r") as f:
                changelog_before = f.read()
        except FileNotFoundError:
            logger.warning("changelog.md not found before generation. It will be created.")

        changelog_gen_output = self._run_command(f"python {os.path.join(self.script_dir, 'changelog_gen.py')} {pyproject_toml_path}", capture_output=True)
        logger.debug(f"Changelog generator output:\n{changelog_gen_output}")

        # Read changelog.md after generation (if not dry run)
        if not self.dry_run:
            with open("changelog.md", "r") as f:
                changelog_after = f.read()
            
            logger.debug("--- changelog.md content before update ---")
            logger.debug(changelog_before)
            logger.debug("--- changelog.md content after update ---")
            logger.debug(changelog_after)
            logger.info("changelog.md has been updated with new entries.")
        else:
            logger.info("[DRY RUN] changelog.md would be updated with new entries.")


    def _stage_changelog(self):
        """Stages changelog.md."""
        logger.info("\n--- Staging changelog.md ---")
        # Only stage if not in dry_run
        if not self.dry_run:
            self._run_command("git add changelog.md")
            logger.info("changelog.md staged.")
        else:
            logger.info("[DRY RUN] Would stage changelog.md")

    def _amend_commit(self):
        """Amends the bump-my-version commit with changelog changes."""
        logger.info("\n--- Amending commit with changelog changes ---")
        # Only amend if not in dry_run
        if not self.dry_run:
            current_commit_hash = self._run_command("git rev-parse HEAD", capture_output=True)
            self._run_command("git commit --amend --no-edit")
            new_commit_hash = self._run_command("git rev-parse HEAD", capture_output=True)
            logger.info(f"Commit {current_commit_hash} amended to {new_commit_hash}.")
        else:
            logger.info("[DRY RUN] Would amend the last commit")

    def _push_changes(self):
        """Pushes changes to remote."""
        logger.info("\n--- Pushing changes to remote ---")
        if not self.dry_run:
            current_branch = self._run_command("git rev-parse --abbrev-ref HEAD", capture_output=True)
            logger.info(f"Pushing branch '{current_branch}' and tags to origin.")
            self._run_command(f"git push --force-with-lease origin {current_branch} --tags")
            logger.info("Changes pushed successfully.")
        else:
            logger.info("[DRY RUN] Would push changes to remote")

    def run(self):
        """Orchestrates the release process."""
        logger.info(f"--- Starting release process for {self.version_part} bump ---")
        if self.dry_run:
            logger.info("--- DRY-RUN MODE: No actual changes will be made to files or Git repository. ---")
            logger.info("--- This mode simulates commands and reports what *would* happen. ---")
        try:
            self._check_clean_working_directory()
            self._bump_version()
            self._generate_changelog()
            self._stage_changelog()
            self._amend_commit()
            self._push_changes()
            logger.info("\n--- Release process complete! ---")
        except ReleaseError as e:
            logger.error(f"\n--- Release process failed ---")
            logger.error(f"Error: {e}")
            sys.exit(1)
        except Exception as e:
            logger.exception(f"\n--- An unexpected error occurred during release process ---")
            logger.error(f"Error: {e}")
            sys.exit(1)

def _print_help():
    """Prints the help message for the release script."""
    help_message = """
Usage: python versioning/release.py <patch|minor|major> [-dr|--dry-run] [-v|--verbose]

This script automates the release process for the project, including:
- Bumping the version number (patch, minor, or major).
- Generating changelog entries based on Git commit history.
- Amending the version bump commit with changelog changes.
- Pushing the updated branch and new tags to the remote repository.

Arguments:
  <patch|minor|major>  Specify the part of the version to bump.
                       - 'patch': Increments the patch version (e.g., 1.0.0 -> 1.0.1)
                       - 'minor': Increments the minor version (e.g., 1.0.0 -> 1.1.0)
                       - 'major': Increments the major version (e.g., 1.0.0 -> 2.0.0)

Options:
  -dr, --dry-run       Simulate the release process without making any actual
                       changes to files or the Git repository. This mode
                       reports what *would* happen.

  -v, --verbose        Enable verbose logging. This will output detailed
                       information about each step, including command executions,
                       stdout/stderr of subprocesses, and file content changes.

  -h, --help           Show this help message and exit.

Examples:
  # Perform a dry run for a patch version bump with verbose logging
  python versioning/release.py patch -dr -v

  # Perform a live minor version bump
  python versioning/release.py minor
"""
    print(help_message)

def main():
    # Configure Loguru for this script
    logger.remove() # Remove default handler
    
    # Determine logging level based on verbose flag
    log_level = "INFO"
    
    # Parse arguments for help, dry_run, and verbose
    args_to_process = sys.argv[1:] # Exclude script name
    
    if "-h" in args_to_process or "--help" in args_to_process:
        _print_help()
        sys.exit(0)

    dry_run = False
    if "-dr" in args_to_process:
        dry_run = True
        args_to_process.remove("-dr")
    elif "--dry-run" in args_to_process:
        dry_run = True
        args_to_process.remove("--dry-run")

    verbose = False
    if "-v" in args_to_process:
        verbose = True
        args_to_process.remove("-v")
    elif "--verbose" in args_to_process:
        verbose = True
        args_to_process.remove("--verbose")

    if verbose:
        log_level = "DEBUG"

    logger.add(sys.stderr, level=log_level, colorize=True,
               format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")
    logger.add("Logs/versioning.log", rotation="10 MB", retention="10 days", compression="zip", level="DEBUG", # Always log DEBUG to file
               format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}")

    if not args_to_process:
        logger.error("Error: Missing version part. Please specify 'patch', 'minor', or 'major'.")
        _print_help()
        sys.exit(1)

    version_part = args_to_process[0]
    
    manager = ReleaseManager(version_part, dry_run, verbose) # Pass verbose flag
    manager.run()

if __name__ == "__main__":
    main()