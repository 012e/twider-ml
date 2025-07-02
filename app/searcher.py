from qdrant_client import models

from .client import app_qdrant
from .config import settings

class HybridSearcher:
    def __init__(self, collection_name: str = None):
        self.collection_name = collection_name or settings.posts_collection_name
        self.qdrant_client = app_qdrant

    def search(self, text: str, offset: int = 0, limit: int = 10):
        search_result = self.qdrant_client.query_points(
            collection_name=self.collection_name,
            query=models.FusionQuery(
                fusion=models.Fusion.RRF  # we are using reciprocal rank fusion here
            ),
            prefetch=[
                models.Prefetch(
                    query=models.Document(text=text, model=settings.content_dense_model_name),
                    using=settings.content_dense_vector_name
                ),
                models.Prefetch(
                    query=models.Document(text=text, model=settings.content_sparse_model_name),
                    using=settings.content_sparse_vector_name
                ),
            ],
            query_filter=None,
            offset=offset,
            limit=limit,
        ).points

        # Select and return metadata
        metadata = [point.id for point in search_result]
        return metadata
