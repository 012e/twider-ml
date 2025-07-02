from typing import List
from uuid import UUID

from nats.aio.msg import Msg
from pydantic import BaseModel
from qdrant_client import models

from app.client import app_qdrant
from app.config import settings
from utils.pydantic_generators import to_pascal_case


class PostCreatedEvent(BaseModel):
    id: UUID
    content: str
    media_urls: list[str]

    model_config = {
        "alias_generator": to_pascal_case,
        "populate_by_name": True,
    }


async def handle_post_created(msgs: list[Msg]):
    data = [PostCreatedEvent.model_validate_json(msg.data) for msg in msgs]
    points = []
    for datum in data:
        content_dense_embedding = models.Document(text=datum.content, model=settings.content_dense_model_name)
        content_sparse_embedding = models.Document(text=datum.content, model=settings.content_sparse_model_name)
        points.append(
            models.PointStruct(
                id=str(datum.id),
                vector={
                    settings.content_dense_vector_name: content_dense_embedding,
                    settings.content_sparse_vector_name: content_sparse_embedding,
                },
                payload={
                    "content": datum.content,
                    "media_urls": [str(url) for url in datum.media_urls],
                },
            )
        )
    print(f"Upserting {len(points)} points to Qdrant")

    app_qdrant.upsert(collection_name=settings.posts_collection_name, points=points)
