import subprocess
import sys
import os
from datetime import datetime
from loguru import logger # Import loguru

class ReleaseError(Exception):
    """Custom exception for release process failures."""
    pass

class ReleaseManager:
    def __init__(self, version_part: str, dry_run: bool = False):
        self.version_part = version_part
        self.dry_run = dry_run
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
        
        logger.info(f"Executing: {full_command}")
        try:
            result = subprocess.run(
                full_command,
                shell=True,
                check=check_error,
                text=True,
                capture_output=capture_output,
                cwd=cwd if cwd else self.original_cwd # Use provided cwd or default to original_cwd
            )
            if capture_output:
                if result.stdout:
                    logger.debug(f"Stdout: {result.stdout.strip()}")
                if result.stderr:
                    logger.warning(f"Stderr: {result.stderr.strip()}")
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

    def _check_clean_working_directory():
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
        self._run_command(f"bump-my-version bump {self.version_part} {dry_run_flag}")

    def _generate_changelog(self):
        """Generates changelog using changelog_gen.py."""
        logger.info("\n--- Generating changelog ---")
        pyproject_toml_path = os.path.join(self.original_cwd, "pyproject.toml")
        # changelog_gen.py doesn't have a dry-run mode, but its output won't be committed if we're in dry_run
        self._run_command(f"python changelog_gen.py {pyproject_toml_path}", cwd=self.script_dir)

    def _stage_changelog(self):
        """Stages changelog.md."""
        logger.info("\n--- Staging changelog.md ---")
        # Only stage if not in dry_run
        if not self.dry_run:
            self._run_command("git add changelog.md")
        else:
            logger.info("[DRY RUN] Would stage changelog.md")

    def _amend_commit(self):
        """Amends the bump-my-version commit with changelog changes."""
        logger.info("\n--- Amending commit with changelog changes ---")
        # Only amend if not in dry_run
        if not self.dry_run:
            self._run_command("git commit --amend --no-edit")
        else:
            logger.info("[DRY RUN] Would amend the last commit")

    def _push_changes(self):
        """Pushes changes to remote."""
        logger.info("\n--- Pushing changes to remote ---")
        if not self.dry_run:
            current_branch = self._run_command("git rev-parse --abbrev-ref HEAD", capture_output=True)
            self._run_command(f"git push --force-with-lease origin {current_branch} --tags")
        else:
            logger.info("[DRY RUN] Would push changes to remote")

    def run(self):
        """Orchestrates the release process."""
        logger.info(f"--- Starting release process for {self.version_part} bump (Dry Run: {self.dry_run}) ---")
        try:
            self._check_clean_working_directory() # Add this check here
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

def main():
    # Configure Loguru for this script
    logger.remove() # Remove default handler
    logger.add(sys.stderr, level="INFO", colorize=True,
               format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")
    logger.add("Logs/versioning.log", rotation="10 MB", retention="10 days", compression="zip", level="DEBUG",
               format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}")

    if len(sys.argv) < 2:
        logger.error("Usage: python versioning/release.py <patch|minor|major> [--dry-run]")
        sys.exit(1)

    version_part = sys.argv[1]
    dry_run = "--dry-run" in sys.argv

    manager = ReleaseManager(version_part, dry_run)
    manager.run()

if __name__ == "__main__":
    main()
