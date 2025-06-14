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
    media_urls: List[UUID]

    model_config = {
        "alias_generator": to_pascal_case,
        "populate_by_name": True,
    }


async def handle_post_created(msgs: list[Msg]):
    data = [PostCreatedEvent.model_validate_json(msg.data) for msg in msgs]
    points = []
    for datum in data:
        dense_document = models.Document(text=datum.content, model=settings.dense_model_name)
        sparse_document = models.Document(text=datum.content, model=settings.sparse_model_name)
        points.append(
            models.PointStruct(
                id=str(datum.id),
                vector={
                    settings.dense_vector_name: dense_document,
                    settings.sparse_vector_name: sparse_document,
                },
                payload={
                    "content": datum.content,
                    "media_urls": [str(url) for url in datum.media_urls],
                },
            )
        )
    print(f"Upserting {len(points)} points to Qdrant")

    app_qdrant.upsert(collection_name=settings.posts_collection_name, points=points)
