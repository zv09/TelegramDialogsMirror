#!/usr/bin/env python3
"""
This module handles command-line argument parsing for the application.
"""

import argparse

def parse_args():
    """Defines and parses command-line arguments."""
    parser = argparse.ArgumentParser(description="Telegram Dialogs Mirror Bot")
    parser.add_argument(
        "-c",
        "--copy",
        action="store_true",
        help="Check and copy missing messages from source to target channels."
    )
    parser.add_argument(
        "-dr",
        "--dry-run",
        action="store_true",
        help="Perform a dry run of the copy mode without making any changes."
    )
    parser.add_argument(
        "-s",
        "--session",
        type=str,
        help="Specify a session file to use."
    )
    return parser.parse_args()
