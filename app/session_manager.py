#!/usr/bin/env python3
"""
This module handles the logic for selecting and managing Telethon session files.
"""

import os
import glob
from loguru import logger

class SessionManager:
    """Manages the discovery and selection of session files."""

    def __init__(self, session_arg: str = None, default_session_name: str = 'pyTelegramDialogsMirror'):
        self.session_arg = session_arg
        self.default_session_name = default_session_name
        self.sessions_dir = 'sessions'

    def _ensure_sessions_dir_exists(self):
        """Checks for the sessions directory and creates it if it doesn't exist."""
        if not os.path.exists(self.sessions_dir):
            logger.info(f"The '{self.sessions_dir}' directory was not found. Creating it now.")
            try:
                os.makedirs(self.sessions_dir)
            except OSError as e:
                logger.critical(f"Failed to create the sessions directory: {e}")
                raise

    def get_session_name(self) -> str:
        """
        Determines the appropriate session file to use based on arguments and existing files.
        Returns the full path to the session file (e.g., 'sessions/my_session').
        """
        self._ensure_sessions_dir_exists()

        # If a session is specified via command-line, use it directly.
        if self.session_arg:
            logger.info(f"Using session specified via command line: '{self.session_arg}'")
            return os.path.join(self.sessions_dir, self.session_arg)

        # Scan for existing .session files
        session_files = glob.glob(os.path.join(self.sessions_dir, '*.session'))

        # If no session files exist, use the default name.
        if not session_files:
            logger.info("No existing session files found. Using default session name.")
            return os.path.join(self.sessions_dir, self.default_session_name)

        # If exactly one session file exists, use it automatically.
        if len(session_files) == 1:
            session_name = os.path.basename(session_files[0]).replace('.session', '')
            logger.info(f"Found one session file. Automatically using: '{session_name}'")
            return os.path.join(self.sessions_dir, session_name)

        # If multiple session files exist, prompt the user to choose.
        return self._prompt_user_to_choose_session(session_files)

    def _prompt_user_to_choose_session(self, session_files: list) -> str:
        """
        Lists available session files and prompts the user to select one.
        Returns the full path to the chosen session file.
        """
        logger.info("Multiple session files found. Please choose which one to use:")
        
        # Strip .session extension for cleaner display
        cleaned_files = [os.path.basename(f).replace('.session', '') for f in session_files]

        for i, session_name in enumerate(cleaned_files):
            print(f"  {i + 1}) {session_name}")

        while True:
            try:
                choice = input(f"Enter your choice (1-{len(cleaned_files)}): ")
                choice_index = int(choice) - 1
                if 0 <= choice_index < len(cleaned_files):
                    chosen_session_name = cleaned_files[choice_index]
                    logger.info(f"You have selected: '{chosen_session_name}'")
                    return os.path.join(self.sessions_dir, chosen_session_name)
                else:
                    logger.warning("Invalid selection. Please try again.")
            except ValueError:
                logger.warning("Invalid input. Please enter a number.")
            except (KeyboardInterrupt, EOFError):
                logger.critical("\nSession selection cancelled by user. Exiting.")
                exit(1)
