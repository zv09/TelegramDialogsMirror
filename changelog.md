# Changelog

All notable changes to this project will be documented in this file.

## [1.5.0] - 2025-07-22

* fix: configure bump-my-version to get logs from git
* feat: add changelog and configure bump-my-version
* fix: uncomment params in env_example.txt
* fix: listen only to specified source channels
* feat: implement lru cache for dialog names
* docs: add configuration section to readme
* opt: reduce memory usage in synchronizer
* docs: add explanation for MAX_CACHE_SIZE
* refactor: simplify forwarder run method
* refactor: split _send_message into smaller methods
* refactor: use get_display_name in _get_dialog_name
* perf: remove connection lock from message_handler to improve performance
* refactor: remove redundant connection lock in forwarder
* fix: pass stats_manager to MessageSynchronizer
* refactor: use specific exception handling in message_handler
* refactor: improve client disconnection and error handling in launcher
* feat: add traceback to main error log
* refactor: improve error handling and connection management in forwarder
* feat: add safeguard to prevent accidental deletion
* fix: improve shutdown handling in synchronizer
* fix: prevent caching of failed initial fetches
* feat: improve retry decorator with jitter and backoff

## [Unreleased]
