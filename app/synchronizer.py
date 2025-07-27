import asyncio
from telethon import TelegramClient
from telethon.tl.types import MessageMediaWebPage, MessageService
from telethon.tl.custom import Button
from loguru import logger

from app.cache import CacheManager
from app.utils import retry_on_telegram_error
from config.config import Settings

class MessageSynchronizer:
    """Synchronizes messages between a source and target channel."""

    def __init__(self, client: TelegramClient, cache_manager: CacheManager, forwarder, stats_manager):
        self.client = client
        self.cache_manager = cache_manager
        self.forwarder = forwarder
        self.stats_manager = stats_manager
        self.settings = Settings()

    def _parse_signature_button(self, message):
        """Parses the signature from an invisible button on a message."""
        if not message or not message.buttons:
            return None
        try:
            data = message.buttons[0][0].data.decode('utf-8')
            source_id, message_id = map(int, data.split('.'))
            return source_id, message_id
        except (AttributeError, IndexError, ValueError):
            return None

    @retry_on_telegram_error()
    async def _get_source_state(self, channel_id):
        """Fetches the state of the source channel, returning a list of message IDs."""
        cache_key = self.cache_manager.get_channel_state_key(channel_id)
        cached_data = self.cache_manager.get(cache_key)
        if cached_data is not None:
            logger.info(f"Loaded source channel state for {channel_id} from cache.")
            return cached_data

        logger.info(f"Building initial cache for source channel {channel_id}.")
        try:
            message_ids = [msg.id async for msg in self.client.iter_messages(channel_id)]
            self.cache_manager.set(cache_key, message_ids)
            logger.info(f"Fetched and cached state for source channel {channel_id}.")
            return message_ids
        except Exception as e:
            logger.error(f"Failed to fetch initial state for {channel_id}: {e}")
            return []

    @retry_on_telegram_error()
    async def synchronize(self, source_channel_id: int, target_channel_id: int, shutdown_event: asyncio.Event):
        logger.info(f"Starting synchronization: {source_channel_id} -> {target_channel_id}")

        source_message_ids = await self._get_source_state(source_channel_id)
        
        logger.info(f"Fetching live state for destination channel {target_channel_id}.")
        # Memory optimization: Iterate and store only IDs, not full message objects.
        target_messages_info = []
        async for msg in self.client.iter_messages(target_channel_id):
            sig = self._parse_signature_button(msg)
            original_source_id = sig[1] if sig and sig[0] == source_channel_id else -1
            target_messages_info.append({'original_id': original_source_id, 'target_id': msg.id})

        # Messages are fetched newest to oldest. Reverse to compare from the start.
        source_message_ids.reverse()
        target_messages_info.reverse()

        target_original_ids = [info['original_id'] for info in target_messages_info]

        logger.debug(f"Source IDs ({len(source_message_ids)}): {source_message_ids}")
        logger.debug(f"Target's Original IDs ({len(target_original_ids)}): {target_original_ids}")

        divergence_index = 0
        while (divergence_index < len(source_message_ids) and 
               divergence_index < len(target_original_ids)):
            if source_message_ids[divergence_index] != target_original_ids[divergence_index]:
                break
            divergence_index += 1

        logger.info(f"Divergence found at index {divergence_index}.")

        if divergence_index < len(target_messages_info):
            num_to_delete = len(target_messages_info) - divergence_index
            logger.info(f"Target channel has {num_to_delete} incorrect messages. Deleting them.")
            
            target_msgs_to_delete = [
                info['target_id'] for info in target_messages_info[divergence_index:] if info['original_id'] != -1
            ]
            
            if target_msgs_to_delete:
                self.stats_manager.add_messages_deleted(len(target_msgs_to_delete))
                await retry_on_telegram_error()(self.client.delete_messages)(target_channel_id, target_msgs_to_delete)

        resend_count = len(source_message_ids) - divergence_index
        if resend_count > 0:
            first_msg_id = source_message_ids[divergence_index]
            logger.info(f"Starting copy from source message ID: {first_msg_id}.")
            
            ids_to_resend = source_message_ids[divergence_index:]
            batch_size = self.forwarder.settings.BATCH_SIZE

            for i in range(0, len(ids_to_resend), batch_size):
                batch_ids = ids_to_resend[i:i + batch_size]
                logger.info(f"Processing batch {i//batch_size + 1}/{(len(ids_to_resend) + batch_size - 1)//batch_size}")
                
                messages_to_resend = await self.client.get_messages(source_channel_id, ids=batch_ids)

                for message in sorted(filter(None, messages_to_resend), key=lambda m: m.id):
                    if shutdown_event.is_set():
                        logger.warning("Shutdown signal received, stopping synchronization.")
                        return

                    if self.settings.SKIP_SERVICE_MESSAGES and isinstance(message, MessageService):
                        logger.info(f"Skipping service message {message.id} from {source_channel_id}.")
                        continue

                    try:
                        await self.forwarder._send_message(target_channel_id, message, source_channel_id)
                        logger.info(f"Resent message {message.id} from {source_channel_id}.")
                        self.stats_manager.add_messages_resent(1)
                        await asyncio.sleep(self.forwarder.settings.SEND_DELAY)
                    except Exception as e:
                        logger.error(f"Failed to resend message {message.id}: {e}")
                        self.stats_manager.increment_forward_failure()
                
                if shutdown_event.is_set():
                    logger.warning("Shutdown signal received, stopping synchronization.")
                    return
                logger.info("Batch sent. Pausing for 5 seconds...")
                await asyncio.sleep(5)

        logger.info(f"Synchronization from {source_channel_id} to {target_channel_id} complete.")