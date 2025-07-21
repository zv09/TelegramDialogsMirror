import asyncio
from telethon import TelegramClient
from telethon.tl.types import MessageMediaWebPage, MessageService
from telethon.tl.custom import Button
from loguru import logger

from app.cache import CacheManager

class MessageSynchronizer:
    """Synchronizes messages between a source and target channel."""

    def __init__(self, client: TelegramClient, cache_manager: CacheManager, forwarder):
        self.client = client
        self.cache_manager = cache_manager
        self.forwarder = forwarder

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

    async def _get_source_state(self, channel_id):
        """Fetches the state of the source channel, returning a list of message IDs."""
        cache_key = self.cache_manager.get_channel_state_key(channel_id)
        cached_data = self.cache_manager.get(cache_key)
        if cached_data is not None:
            logger.info(f"Loaded source channel state for {channel_id} from cache.")
            return cached_data

        logger.info(f"Building initial cache for source channel {channel_id}.")
        message_ids = [msg.id async for msg in self.client.iter_messages(channel_id)]
        self.cache_manager.set(cache_key, message_ids)
        logger.info(f"Fetched and cached state for source channel {channel_id}.")
        return message_ids

    async def synchronize(self, source_channel_id: int, target_channel_id: int, shutdown_event: asyncio.Event):
        logger.info(f"Starting synchronization: {source_channel_id} -> {target_channel_id}")

        source_message_ids = await self._get_source_state(source_channel_id)
        
        logger.info(f"Fetching live state for destination channel {target_channel_id}.")
        all_target_msgs = await self.client.get_messages(target_channel_id, limit=None)

        source_message_ids.reverse()
        all_target_msgs.reverse()

        target_original_ids = []
        for msg in all_target_msgs:
            sig = self._parse_signature_button(msg)
            if sig and sig[0] == source_channel_id:
                target_original_ids.append(sig[1])
            else:
                target_original_ids.append(-1)

        logger.debug(f"Source IDs ({len(source_message_ids)}): {source_message_ids}")
        logger.debug(f"Target's Original IDs ({len(target_original_ids)}): {target_original_ids}")

        divergence_index = 0
        while (divergence_index < len(source_message_ids) and \
               divergence_index < len(target_original_ids)):
            if source_message_ids[divergence_index] != target_original_ids[divergence_index]:
                break
            divergence_index += 1

        logger.info(f"Divergence found at index {divergence_index}.")

        if divergence_index < len(all_target_msgs):
            logger.info(f"Target channel has {len(all_target_msgs) - divergence_index} incorrect messages. Deleting them.")
            target_msgs_to_delete = [msg.id for msg in all_target_msgs[divergence_index:]]
            if target_msgs_to_delete:
                await self.client.delete_messages(target_channel_id, target_msgs_to_delete)

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
                    try:
                        await self.forwarder._send_message(target_channel_id, message, source_channel_id)
                        logger.info(f"Resent message {message.id} from {source_channel_id}.")
                        await asyncio.sleep(self.forwarder.settings.SEND_DELAY)
                    except Exception as e:
                        logger.error(f"Failed to resend message {message.id}: {e}")
                
                logger.info("Batch sent. Pausing for 5 seconds...")
                await asyncio.sleep(5)

        logger.info(f"Synchronization from {source_channel_id} to {target_channel_id} complete.")