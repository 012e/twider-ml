from qdrant_client import models

from .client import app_qdrant

class HybridSearcher:
    DENSE_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    SPARSE_MODEL = "prithivida/Splade_PP_en_v1"
    
    def __init__(self, collection_name):
        self.collection_name = collection_name
        self.qdrant_client =app_qdrant

    def search(self, text: str, offset: int = 0, limit: int = 10):
        search_result = self.qdrant_client.query_points(
            collection_name=self.collection_name,
            query=models.FusionQuery(
                fusion=models.Fusion.RRF  # we are using reciprocal rank fusion here
            ),
            prefetch=[
                models.Prefetch(
                    query=models.Document(text=text, model=self.DENSE_MODEL),
                    using="dense"
                ),
                models.Prefetch(
                    query=models.Document(text=text, model=self.SPARSE_MODEL),
                    using="sparse"
                ),
            ],
            query_filter=None,
            offset=offset,
            limit=limit,
        ).points

        # Select and return metadata
        metadata = [point.id for point in search_result]
        return metadata
