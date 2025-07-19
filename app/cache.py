import json
import os
from loguru import logger

class CacheManager:
    """Handles all caching operations for the application."""

    def __init__(self, cache_dir="cache"):
        self.cache_dir = cache_dir
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            logger.info(f"Cache directory created at {self.cache_dir}")

    def get_channel_state_key(self, channel_id: int) -> str:
        """Returns the consistent cache key for a channel's state."""
        return f"channel_state_v9_{channel_id}"

    def _get_cache_filepath(self, key: str) -> str:
        """Generates the file path for a given cache key."""
        return os.path.join(self.cache_dir, f"{key}.json")

    def get(self, key: str):
        """Retrieves an item from the cache."""
        filepath = self._get_cache_filepath(key)
        if not os.path.exists(filepath):
            return None
        try:
            with open(filepath, 'r') as f:
                logger.debug(f"Cache hit for key: {key}")
                return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            logger.warning(f"Could not read cache file for key {key}: {e}")
            return None

    def set(self, key: str, data):
        """Saves an item to the cache, overwriting existing data."""
        filepath = self._get_cache_filepath(key)
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=4)
                logger.debug(f"Cached data for key: {key}")
        except IOError as e:
            logger.error(f"Could not write to cache file for key {key}: {e}")

    def append_to_list(self, key: str, item):
        """Appends an item to a list in the cache. Creates the list if it doesn't exist."""
        data = self.get(key) or []
        if isinstance(data, list):
            data.append(item)
            self.set(key, data)
        else:
            logger.error(f"Cannot append to cache key {key} as it is not a list.")
