import asyncio
import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.api import router as api_router
from app.config import settings
from events import NATSConsumer
from processing.post import handle_post_created

# Configure logging
logging.basicConfig(level=getattr(logging, settings.log_level.upper()))
logger = logging.getLogger(__name__)

# Global consumer instance
consumer: NATSConsumer | None = None


@asynccontextmanager
async def lifespan(_app: FastAPI):
    global consumer
    logger.info("Starting ML Search Service...")

    # Initialize and start NATS consumer with all required parameters
    consumer = NATSConsumer(
        message_handler=handle_post_created,
        nats_url=settings.nats_url,
        stream_name="twider-stream",
        subject="post.created.*",
        durable_name="twider-durable-subscription",
        batch_size=10,
        timeout=1.0
    )
    task = asyncio.create_task(consumer.run())
    logger.info("NATS consumer task started")

    yield

    logger.info("Shutting down ML Search Service...")
    if consumer:
        await consumer.disconnect()
    logger.info("Shutdown complete")


# Initialize FastAPI app
app = FastAPI(
    title="ML Search Service",
    description="Machine Learning powered search service for posts",
    version="0.1.0",
    lifespan=lifespan,
)

# Include API routes
app.include_router(api_router)


@app.get("/")
async def root():
    return {"message": "ML Search Service is running!", "version": "0.1.0"}


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        log_level=settings.log_level,
    )
