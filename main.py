import asyncio
import nats
import uvicorn
from fastapi import FastAPI

from processing.post import handle_post_created

# Initialize FastAPI app
app = FastAPI()

# NATS consumer function
async def run_nats_consumer():
    nc = None
    try:
        nc = await nats.connect("localhost")
        js = nc.jetstream()

        # Ensure the stream exists (create if not, update if exists)
        await js.add_stream(name="twider-stream", subjects=["post.created.*"], exist_ok=True)

        psub = await js.pull_subscribe("post.created.*", stream="twider-stream") # Specify the stream name
        print("NATS consumer started, listening for messages on 'post.created.*'")
        while True:
            try:
                msgs = await psub.fetch(10, timeout=1)
                if msgs:
                    print(f"Received {len(msgs)} NATS messages.")
                    await handle_post_created(msgs)
                    for msg in msgs:
                        await msg.ack()
                await asyncio.sleep(0.1) # Small sleep to prevent busy-waiting
            except asyncio.TimeoutError:
                # No messages in the last second, continue polling
                pass
            except Exception as e:
                print(f"Error in NATS consumer: {e}")
                await asyncio.sleep(5) # Wait before retrying in case of an error
    except Exception as e:
        print(f"Failed to connect to NATS or initialize consumer: {e}")
    finally:
        if nc:
            await nc.close()
            print("NATS connection closed.")

# FastAPI endpoint (example)
@app.get("/")
async def read_root():
    return {"message": "FastAPI is running!"}

# Main function to run both services
async def main():
    # Create the NATS consumer task
    nats_task = asyncio.create_task(run_nats_consumer())

    # Configure Uvicorn server
    config = uvicorn.Config(app, host="0.0.0.0", port=8000)
    server = uvicorn.Server(config)

    # Run the Uvicorn server in the current event loop
    # You can't simply await server.serve() if you also want to run other tasks
    # in the same main function easily.
    # Instead, we'll let uvicorn's run() handle the event loop, and we'll start
    # our nats_task before it.
    
    # Alternatively, for more fine-grained control or if you want to explicitly await
    # server.serve() in a truly concurrent manner within a larger async function:
    # server_task = asyncio.create_task(server.serve())
    # await asyncio.gather(nats_task, server_task)
    
    # However, the standard way to run FastAPI with Uvicorn when you have other
    # async tasks is to let Uvicorn manage the loop and start your background tasks
    # on its startup event.

    # Start FastAPI with Uvicorn
    # This will block until the server is stopped
    await server.serve()

if __name__ == '__main__':
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
