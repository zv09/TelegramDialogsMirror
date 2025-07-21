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
    return parser.parse_args()
