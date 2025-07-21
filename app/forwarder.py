#!/usr/bin/env python3
"""
This script handles the live forwarding of messages.
"""

import asyncio
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaWebPage, MessageService
from telethon.tl.custom import Button
from loguru import logger

from config.config import Settings
from app.cache import CacheManager

class Forwarder:
    """Encapsulates the Telegram client and message forwarding logic."""

    def __init__(self, settings: Settings, cache_manager: CacheManager):
        self.settings = settings
        self.client = self._create_client()
        self.cache_manager = cache_manager
        self._dialog_name_cache = {}

    def _create_client(self):
        """Creates and returns a Telegram client instance."""
        return TelegramClient(self.settings.SESSION_NAME, self.settings.API_ID, self.settings.API_HASH)

    async def _get_dialog_name(self, entity_id):
        """Fetches and caches the name of a dialog."""
        if not entity_id: return "(Unknown)"
        if entity_id in self._dialog_name_cache:
            return self._dialog_name_cache[entity_id]
        try:
            entity = await self.client.get_entity(entity_id)
            name = getattr(entity, 'title', None) or getattr(entity, 'first_name', None) or getattr(entity, 'username', f"ID: {entity_id}")
            if hasattr(entity, 'last_name') and entity.last_name:
                name += f" {entity.last_name}"
            self._dialog_name_cache[entity_id] = name
            return name
        except Exception as e:
            logger.warning(f"Could not get name for entity {entity_id}: {e}")
            return "(Unknown)"

    async def _send_message(self, target_channel_id, message, source_channel_id):
        """Centralized method to send or forward a message."""
        signature_data = f"{source_channel_id}.{message.id}".encode()
        signature_button = Button.inline(" ", data=signature_data)

        if isinstance(message, MessageService):
            logger.info(f"System message in {source_channel_id}. Forwarding placeholder.")
            text = f"System Message: {message.text}"
            await self.client.send_message(target_channel_id, text, buttons=signature_button)
        else:
            sender = await message.get_sender()
            sender_name = await self._get_dialog_name(sender.id)
            logger.info(f"Forwarding message {message.id} from {source_channel_id} to {target_channel_id}.")
            
            header = f"ID: {sender.id} | Author: {sender_name}\ndatetime: {message.date.isoformat().replace('T', ' ')}"
            caption = f"{header}\n\n{message.text or ''}"

            if message.media and not isinstance(message.media, MessageMediaWebPage):
                await self.client.send_file(target_channel_id, message.media, caption=caption, buttons=signature_button)
            else:
                await self.client.send_message(target_channel_id, caption, link_preview=True, buttons=signature_button)

    async def message_handler(self, event):
        """Handles new messages from a source channel and forwards them to the target."""
        message = event.message
        source_channel_id = event.chat_id
        target_channel_id = next((tgt for src, tgt in self.settings.CHANNEL_MAPPINGS if src == source_channel_id), None)

        if not target_channel_id:
            logger.warning(f"No target channel found for source {source_channel_id}. Skipping.")
            return

        try:
            await self._send_message(target_channel_id, message, source_channel_id)

            # Live-update the cache using the unified key
            cache_key = self.cache_manager.get_channel_state_key(source_channel_id)
            self.cache_manager.append_to_list(cache_key, message.id)
            logger.info(f"Successfully forwarded message {message.id} and updated cache.")
            await asyncio.sleep(1)

        except Exception as e:
            logger.error(f"An unexpected error occurred while handling message {message.id}: {e}")

    async def run(self, shutdown_event: asyncio.Event, synchronizer):
        """Runs the Telegram client and listens for messages."""
        logger.info("Client starting...")
        while not shutdown_event.is_set():
            try:
                await self.client.start()
                logger.info("Client started successfully. Listening for messages...")

                for source_channel, target_channel in self.settings.CHANNEL_MAPPINGS:
                    self.client.add_event_handler(self.message_handler, events.NewMessage(chats=source_channel))
                    source_name = await self._get_dialog_name(source_channel)
                    target_name = await self._get_dialog_name(target_channel)
                    logger.info(f"Registered handler: {source_name} (ID: {source_channel}) -> {target_name} (ID: {target_channel})")

                logger.info("Awaiting new events...")
                await shutdown_event.wait()
            except telethon.errors.rpcerrorlist.PersistentTimestampOutdatedError:
                logger.warning("Persistent timestamp outdated. Triggering full resynchronization...")
                for source, target in self.settings.CHANNEL_MAPPINGS:
                    await synchronizer.synchronize(source, target, shutdown_event)
                logger.info("Resynchronization complete. Restarting live forwarding...")
            except Exception as e:
                logger.error(f"An unexpected error occurred: {e}")
                break  # Exit on other unexpected errors
            finally:
                if self.client.is_connected():
                    await self.client.disconnect()
                logger.info("Client stopped.")