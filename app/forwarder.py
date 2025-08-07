#!/usr/bin/env python3
"""
This script handles the live forwarding of messages.
"""

import asyncio
from collections import OrderedDict
import pytz
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaWebPage, MessageService, MessageActionPinMessage, MessageActionChatAddUser, MessageActionChatDeleteUser, MessageActionChatJoinedByLink, MessageActionPinMessage, MessageActionChatAddUser, MessageActionChatDeleteUser, MessageActionChatJoinedByLink
from telethon.tl.custom import Button
from telethon.utils import get_display_name
from loguru import logger

from config.config import Settings
from app.cache import CacheManager

from app.utils import retry_on_telegram_error

class Forwarder:
    """Encapsulates the Telegram client and message forwarding logic."""

    def __init__(self, client: TelegramClient, settings: Settings, cache_manager: CacheManager, stats_manager):
        self.client = client
        self.settings = settings
        self.cache_manager = cache_manager
        self.stats_manager = stats_manager
        self._dialog_name_cache = OrderedDict()

    @retry_on_telegram_error()
    async def _get_dialog_name(self, entity_id):
        """Fetches and caches the name of a dialog using an LRU cache."""
        if not entity_id: return "(Unknown)"
        if entity_id in self._dialog_name_cache:
            self._dialog_name_cache.move_to_end(entity_id)
            return self._dialog_name_cache[entity_id]
        try:
            entity = await self.client.get_entity(entity_id)
            name = get_display_name(entity)
            self._dialog_name_cache[entity_id] = name
            if len(self._dialog_name_cache) > self.settings.MAX_CACHE_SIZE:
                self._dialog_name_cache.popitem(last=False)
            return name
        except Exception as e:
            logger.warning(f"Could not get name for entity {entity_id}: {e}")
            return "(Unknown)"

    @retry_on_telegram_error()
    async def _forward_system_message(self, target_channel_id, message, source_channel_id):
        """Formats and forwards a system message, making it more descriptive."""
        action = message.action
        text = "System Message: "

        if isinstance(action, MessageActionPinMessage):
            logger.info(f"Pinned message notification in {source_channel_id}. Fetching original message.")
            pinned_msg = await self.client.get_messages(source_channel_id, ids=action.message_id)
            if pinned_msg:
                sender = await pinned_msg.get_sender()
                sender_name = await self._get_dialog_name(sender.id)
                header = f"📌 **Message Pinned**\n**From:** {sender_name}"
                caption = f"{header}\n\n{pinned_msg.text or ''}"
                signature_data = f"{source_channel_id}.{pinned_msg.id}".encode()
                signature_button = Button.inline(" ", data=signature_data)

                if pinned_msg.media and not isinstance(pinned_msg.media, MessageMediaWebPage):
                    await self.client.send_file(target_channel_id, pinned_msg.media, caption=caption, buttons=signature_button, parse_mode='md')
                else:
                    await self.client.send_message(target_channel_id, caption, link_preview=True, buttons=signature_button, parse_mode='md')
            else:
                logger.warning(f"Could not fetch pinned message {action.message_id} from {source_channel_id}.")
                await self.client.send_message(target_channel_id, "**System Message:**\n_A message was pinned, but it could not be fetched._", parse_mode='md')
            return # We have handled the pin action completely

        elif isinstance(action, MessageActionChatAddUser):
            user = await self.client.get_entity(action.user_id)
            text = f"➡️ \"{get_display_name(user)}\" joined the chat."
        elif isinstance(action, MessageActionChatDeleteUser):
            user = await self.client.get_entity(action.user_id)
            text = f"⬅️ \"{get_display_name(user)}\" left the chat."
        elif isinstance(action, MessageActionChatJoinedByLink):
            user = await self.client.get_entity(action.user_id)
            inviter = await self.client.get_entity(action.inviter_id)
            text = f"🔗 \"{get_display_name(user)}\" joined via link from \"{get_display_name(inviter)}\"."
        elif hasattr(action, 'title'):
            text = f"✏️ Chat title was changed to \"{action.title}\""
        elif hasattr(action, 'photo'):
            text = "🖼️ Chat photo was changed."
        else:
            text = "⚙️ An unhandled system message occurred."

        logger.info(f"System message in {source_channel_id}: {text}")
        signature_data = f"{source_channel_id}.{message.id}".encode()
        signature_button = Button.inline(" ", data=signature_data)
        await self.client.send_message(target_channel_id, f"**System Message:**\n_{text}_", buttons=signature_button, parse_mode='md')

    @retry_on_telegram_error()
    async def _forward_regular_message(self, target_channel_id, message, source_channel_id):
        """Forwards a regular message."""
        sender = await message.get_sender()
        sender_name = await self._get_dialog_name(sender.id)
        logger.info(f"Forwarding message {message.id} from {source_channel_id} to {target_channel_id}.")

        try:
            tz = pytz.timezone(self.settings.TIMEZONE)
        except pytz.UnknownTimeZoneError:
            logger.warning(f"Unknown timezone '{self.settings.TIMEZONE}' in settings, defaulting to UTC.")
            tz = pytz.utc

        localized_date = message.date.astimezone(tz)
        author_details = f"@{sender.username} | {sender_name}" if sender.username else sender_name
        header = f"ID: {sender.id} | Author: {author_details}\ndatetime: {localized_date.strftime('%Y-%m-%d %H:%M:%S%z')}"
        caption = f"{header}\n\n{message.text or ''}"
        signature_data = f"{source_channel_id}.{message.id}".encode()
        signature_button = Button.inline(" ", data=signature_data)

        if message.media and not isinstance(message.media, MessageMediaWebPage):
            await self.client.send_file(target_channel_id, message.media, caption=caption, buttons=signature_button)
        else:
            await self.client.send_message(target_channel_id, caption, link_preview=True, buttons=signature_button)

    async def _send_message(self, target_channel_id, message, source_channel_id):
        """Centralized method to send or forward a message."""
        if isinstance(message, MessageService):
            await self._forward_system_message(target_channel_id, message, source_channel_id)
            self.stats_manager.increment_system_messages()
        else:
            await self._forward_regular_message(target_channel_id, message, source_channel_id)

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
            self.stats_manager.increment_forward_success()
            await asyncio.sleep(1)

        except (ConnectionError, TimeoutError) as e:
            logger.warning(f"Connection error while handling message {message.id}: {e}")
            self.stats_manager.increment_forward_failure()
        except RPCError as e:
            logger.error(f"A Telegram API error occurred while handling message {message.id}: {e}")
            self.stats_manager.increment_forward_failure()
        except Exception as e:
            logger.error(f"An unexpected error occurred while handling message {message.id}: {e}")
            self.stats_manager.increment_forward_failure()

    async def run(self, shutdown_event: asyncio.Event, synchronizer):
        """Runs the Telegram client and listens for messages."""
        logger.info("Client starting...")
        
        # Listen only to the specified source channels for efficiency.
        source_channels = [source for source, target in self.settings.CHANNEL_MAPPINGS]
        self.client.add_event_handler(self.message_handler, events.NewMessage(chats=source_channels))

        async with self.client:
            logger.info("Client started successfully. Listening for messages...")

            for source_channel, target_channel in self.settings.CHANNEL_MAPPINGS:
                source_name = await self._get_dialog_name(source_channel)
                target_name = await self._get_dialog_name(target_channel)
                logger.info(f"Registered handler: {source_name} (ID: {source_channel}) -> {target_name} (ID: {target_channel})")

            logger.info("Awaiting new events...")
            await shutdown_event.wait()