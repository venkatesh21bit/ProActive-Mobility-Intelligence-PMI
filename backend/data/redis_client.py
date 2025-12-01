"""
Redis client for streaming telemetry data
"""

import redis.asyncio as redis
import json
import logging
from typing import Dict, List, Optional
from config.settings import settings

logger = logging.getLogger(__name__)


class RedisStreamClient:
    """Redis Streams client for telemetry ingestion"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.stream_name = settings.redis_stream_name
        
    async def connect(self):
        """Connect to Redis"""
        try:
            self.redis_client = await redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("Connected to Redis successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Disconnected from Redis")
    
    async def add_to_stream(self, data: Dict, stream_name: Optional[str] = None) -> str:
        """
        Add data to Redis Stream
        
        Args:
            data: Dictionary of data to add
            stream_name: Stream name (defaults to settings.redis_stream_name)
            
        Returns:
            Message ID
        """
        if not self.redis_client:
            raise RuntimeError("Redis client not connected")
        
        stream = stream_name or self.stream_name
        
        try:
            # Convert nested data to JSON strings
            stream_data = {k: json.dumps(v) if isinstance(v, (dict, list)) else str(v) 
                          for k, v in data.items()}
            
            message_id = await self.redis_client.xadd(stream, stream_data)
            logger.debug(f"Added message {message_id} to stream {stream}")
            return message_id
        except Exception as e:
            logger.error(f"Error adding to stream: {e}")
            raise
    
    async def read_stream(
        self, 
        stream_name: Optional[str] = None,
        count: int = 10,
        block: Optional[int] = None,
        last_id: str = "0"
    ) -> List[tuple]:
        """
        Read messages from Redis Stream
        
        Args:
            stream_name: Stream name to read from
            count: Maximum number of messages to read
            block: Milliseconds to block (None for non-blocking)
            last_id: Last message ID (use '0' for all, '$' for new)
            
        Returns:
            List of (message_id, data) tuples
        """
        if not self.redis_client:
            raise RuntimeError("Redis client not connected")
        
        stream = stream_name or self.stream_name
        
        try:
            messages = await self.redis_client.xread(
                {stream: last_id},
                count=count,
                block=block
            )
            
            if messages:
                # messages format: [(stream_name, [(msg_id, data), ...])]
                return messages[0][1]
            return []
        except Exception as e:
            logger.error(f"Error reading from stream: {e}")
            raise
    
    async def create_consumer_group(
        self,
        group_name: str,
        stream_name: Optional[str] = None,
        start_id: str = "0"
    ):
        """
        Create a consumer group for the stream
        
        Args:
            group_name: Name of the consumer group
            stream_name: Stream name
            start_id: Starting position ('0' for beginning, '$' for new messages)
        """
        if not self.redis_client:
            raise RuntimeError("Redis client not connected")
        
        stream = stream_name or self.stream_name
        
        try:
            await self.redis_client.xgroup_create(
                stream,
                group_name,
                id=start_id,
                mkstream=True
            )
            logger.info(f"Created consumer group '{group_name}' for stream '{stream}'")
        except redis.ResponseError as e:
            if "BUSYGROUP" in str(e):
                logger.info(f"Consumer group '{group_name}' already exists")
            else:
                logger.error(f"Error creating consumer group: {e}")
                raise
    
    async def read_group(
        self,
        group_name: str,
        consumer_name: str,
        stream_name: Optional[str] = None,
        count: int = 10,
        block: Optional[int] = 5000
    ) -> List[tuple]:
        """
        Read messages as part of a consumer group
        
        Args:
            group_name: Consumer group name
            consumer_name: Consumer identifier
            stream_name: Stream name
            count: Maximum messages to read
            block: Milliseconds to block
            
        Returns:
            List of (message_id, data) tuples
        """
        if not self.redis_client:
            raise RuntimeError("Redis client not connected")
        
        stream = stream_name or self.stream_name
        
        try:
            messages = await self.redis_client.xreadgroup(
                group_name,
                consumer_name,
                {stream: ">"},
                count=count,
                block=block
            )
            
            if messages:
                return messages[0][1]
            return []
        except Exception as e:
            logger.error(f"Error reading from group: {e}")
            raise
    
    async def acknowledge(
        self,
        group_name: str,
        message_id: str,
        stream_name: Optional[str] = None
    ):
        """
        Acknowledge message processing
        
        Args:
            group_name: Consumer group name
            message_id: Message ID to acknowledge
            stream_name: Stream name
        """
        if not self.redis_client:
            raise RuntimeError("Redis client not connected")
        
        stream = stream_name or self.stream_name
        
        try:
            await self.redis_client.xack(stream, group_name, message_id)
            logger.debug(f"Acknowledged message {message_id}")
        except Exception as e:
            logger.error(f"Error acknowledging message: {e}")
            raise
    
    async def get_stream_info(self, stream_name: Optional[str] = None) -> Dict:
        """Get information about a stream"""
        if not self.redis_client:
            raise RuntimeError("Redis client not connected")
        
        stream = stream_name or self.stream_name
        
        try:
            info = await self.redis_client.xinfo_stream(stream)
            return info
        except Exception as e:
            logger.error(f"Error getting stream info: {e}")
            return {}


# Global Redis client instance
redis_stream_client = RedisStreamClient()
