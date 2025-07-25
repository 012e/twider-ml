import asyncio
import logging
from typing import Optional, Callable, Awaitable

import nats
from nats.aio.client import Client
from nats.aio.msg import Msg
from nats.js import JetStreamContext

logger = logging.getLogger(__name__)


class NATSConsumer:
    """NATS JetStream consumer for handling post events."""
    
    def __init__(
        self, 
        message_handler: Callable[[list[Msg]], Awaitable[None]],
        nats_url: str,
        stream_name: str,
        subject: str,
        durable_name: str,
        batch_size: int,
        timeout: float
    ):
        self.nats_url = nats_url
        self.stream_name = stream_name
        self.subject = subject
        self.durable_name = durable_name
        self.batch_size = batch_size
        self.timeout = timeout
        self.message_handler = message_handler
        
        self._nc: Client | None = None
        self._js: JetStreamContext | None = None
        self._running = False

    async def connect(self) -> None:
        """Establish connection to NATS and set up JetStream."""
        try:
            self._nc = await nats.connect(self.nats_url)
            self._js = self._nc.jetstream()
            
            # Ensure the stream exists
            await self._js.add_stream(
                name=self.stream_name, 
                subjects=[self.subject]
            )
            
            logger.info(f"Connected to NATS at {self.nats_url}")
        except Exception as e:
            logger.error(f"Failed to connect to NATS: {e}")
            raise

    async def disconnect(self) -> None:
        """Close NATS connection."""
        self._running = False
        if self._nc:
            await self._nc.close()
            logger.info("NATS connection closed")

    async def start_consuming(self) -> None:
        """Start consuming messages from the stream."""
        if not self._js:
            raise RuntimeError("Must call connect() before start_consuming()")
        
        try:
            psub = await self._js.pull_subscribe(
                self.subject,
                stream=self.stream_name,
                durable=self.durable_name,
            )
            
            logger.info(f"NATS consumer started, listening for messages on '{self.subject}'")
            self._running = True
            
            while self._running:
                try:
                    msgs = await psub.fetch(self.batch_size, timeout=self.timeout)
                    if msgs:
                        logger.info(f"Received {len(msgs)} NATS messages")
                        await self.message_handler(msgs)
                        for msg in msgs:
                            await msg.ack()
                    
                    await asyncio.sleep(0.1)  # Prevent busy-waiting
                    
                except asyncio.TimeoutError:
                    # No messages in the timeout period, continue polling
                    continue
                except Exception as e:
                    logger.error(f"Error processing messages: {e}")
                    await asyncio.sleep(5)  # Wait before retrying
                    
        except Exception as e:
            logger.error(f"Error in NATS consumer: {e}")
            raise

    async def run(self) -> None:
        """Run the consumer with automatic connection management."""
        try:
            await self.connect()
            await self.start_consuming()
        except Exception as e:
            logger.error(f"Consumer failed: {e}")
        finally:
            await self.disconnect()
