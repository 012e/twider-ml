import asyncio
from typing import List

import nats
import uvicorn
from fastapi import FastAPI, Query
from pydantic import BaseModel

from app.searcher import HybridSearcher
from processing.post import handle_post_created

# Initialize FastAPI app
app = FastAPI()

# Initialize searcher
searcher = HybridSearcher("posts")


class PostSearchResult(BaseModel):
    id: str
    content: str
    media_urls: List[str]


class SearchResponse(BaseModel):
    results: List[PostSearchResult]
    total: int
    offset: int
    limit: int


@app.get("/search", response_model=SearchResponse)
async def search_posts(
    q: str = Query(..., description="Search query"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(15, ge=1, le=100, description="Number of results to return"),
):
    # Get point IDs from searcher
    point_ids = searcher.search(text=q, offset=offset, limit=limit)

    # Get full point data including payload
    points = searcher.qdrant_client.retrieve(
        collection_name="posts", ids=point_ids, with_payload=True
    )

    # Convert to response format
    results = [
        PostSearchResult(
            id=point.id,
            content=point.payload["content"],
            media_urls=point.payload["media_urls"],
        )
        for point in points
    ]

    return SearchResponse(
        results=results, total=len(results), offset=offset, limit=limit
    )


# NATS consumer function
async def run_nats_consumer():
    nc = None
    try:
        nc = await nats.connect("localhost")
        js = nc.jetstream()

        # Ensure the stream exists (create if not, update if exists)
        await js.add_stream(name="twider-stream", subjects=["post.created.*"])

        psub = await js.pull_subscribe(
            "post.created.*",
            stream="twider-stream",
            durable="twider-durable-subscription",
        )  # Specify the stream name
        print("NATS consumer started, listening for messages on 'post.created.*'")
        while True:
            try:
                msgs = await psub.fetch(10, timeout=1)
                if msgs:
                    print(f"Received {len(msgs)} NATS messages.")
                    await handle_post_created(msgs)
                    for msg in msgs:
                        await msg.ack()
                await asyncio.sleep(0.1)  # Small sleep to prevent busy-waiting
            except asyncio.TimeoutError:
                # No messages in the last second, continue polling
                pass
            except Exception as e:
                print(f"Error in NATS consumer: {e}")
                await asyncio.sleep(5)  # Wait before retrying in case of an error
    except Exception as e:
        print(f"Failed to connect to NATS or initialize consumer: {e}")
    finally:
        if nc:
            await nc.close()
            print("NATS connection closed.")


# FastAPI endpoint (example)
@app.get("/")
async def search():
    return {"message": "FastAPI is running!"}


# Main function to run both services
async def main():
    nats_task = asyncio.create_task(run_nats_consumer())

    config = uvicorn.Config(app, host="0.0.0.0", port=8000)
    server = uvicorn.Server(config)

    asyncio.gather(nats_task, server.serve())


if __name__ == "__main__":
    # It's generally recommended to use uvicorn.run directly for FastAPI applications
    # and leverage FastAPI's startup/shutdown events for background tasks.
    # This ensures Uvicorn manages the event loop correctly.

    # Option 1: Using FastAPI's @app.on_event("startup")
    # This is the recommended and cleaner approach.
    @app.on_event("startup")
    async def startup_event():
        print("FastAPI startup event: Starting NATS consumer...")
        asyncio.create_task(run_nats_consumer())

    uvicorn.run(app, host="0.0.0.0", port=8000)

    # Option 2: Running asyncio.run(main()) directly (less common for production)
    # This works, but uvicorn.run is optimized for running FastAPI.
    # asyncio.run(main())
