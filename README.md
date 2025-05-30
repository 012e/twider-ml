# ML Search Service

A machine learning powered search service for posts using hybrid vector search with Qdrant and real-time event processing via NATS.

## Architecture

The service is now organized with clear separation of concerns:

### Core Components

- **API Layer** (`app/api.py`): FastAPI routes for search endpoints
- **Event Processing** (`events/consumer.py`): NATS JetStream consumer for handling post events
- **Search Engine** (`app/searcher.py`): Hybrid search implementation using dense + sparse vectors
- **Configuration** (`app/config.py`): Centralized configuration management with environment variable support
- **Data Processing** (`processing/post.py`): Post event handlers and vector generation

### Key Features

- **Hybrid Search**: Combines dense and sparse vector search using Reciprocal Rank Fusion (RRF)
- **Real-time Processing**: Processes post creation events via NATS JetStream
- **Configuration Management**: Environment-based configuration with sensible defaults
- **Health Monitoring**: Built-in health check endpoints
- **Clean Architecture**: Separation between API, event handling, and business logic

## Configuration

Environment variables can be used to configure the service:

```bash
# Qdrant
QDRANT_URL=http://localhost:6333

# NATS
NATS_URL=localhost
NATS_STREAM_NAME=twider-stream
NATS_SUBJECT=post.created.*

# API
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=info
```

## Running the Service

```bash
make run
# or
uv run main.py
```

## API Endpoints

- `GET /` - Root endpoint with service info
- `GET /api/v1/search` - Search posts with query parameters
- `GET /api/v1/health` - Health check endpoint

## Development

The service uses:
- FastAPI for the REST API
- NATS JetStream for event processing
- Qdrant for vector search
- Pydantic for configuration and data validation