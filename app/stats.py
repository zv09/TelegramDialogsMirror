#!/usr/bin/env python3
"""
This module contains the StatsManager for tracking application metrics.
"""

from loguru import logger

class StatsManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StatsManager, cls).__new__(cls)
            cls._instance.reset()
        return cls._instance

    def reset(self):
        """Initializes or resets all statistics."""
        self.forward_success = 0
        self.forward_failure = 0
        self.system_messages_forwarded = 0
        self.messages_deleted = 0
        self.messages_resent = 0

    def increment_forward_success(self):
        self.forward_success += 1

    def increment_forward_failure(self):
        self.forward_failure += 1

    def increment_system_messages(self):
        self.system_messages_forwarded += 1

    def add_messages_deleted(self, count):
        self.messages_deleted += count

    def add_messages_resent(self, count):
        self.messages_resent += count

    def log_summary(self):
        """Logs a formatted summary of all collected statistics."""
        logger.info("--- Runtime Summary ---")
        logger.info(f"Successfully Forwarded: {self.forward_success}")
        logger.info(f"Failed to Forward: {self.forward_failure}")
        logger.info(f"System Messages Processed: {self.system_messages_forwarded}")
        if self.messages_deleted > 0:
            logger.info(f"Messages Deleted (Sync): {self.messages_deleted}")
        if self.messages_resent > 0:
            logger.info(f"Messages Resent (Sync): {self.messages_resent}")
        logger.info("-----------------------")

# Create a single instance for the application to use
stats_manager = StatsManager()
