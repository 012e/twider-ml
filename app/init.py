from qdrant_client.models import models
from app.client import app_qdrant
from app.config import settings


def create_collections_if_not_exists():
    """
    Create the 'posts' collection if it does not already exist.
    """
    app_qdrant.create_collection(
        collection_name=settings.posts_collection_name,
        vectors_config={
            settings.content_dense_vector_name: models.VectorParams(
                size=app_qdrant.get_embedding_size(settings.content_dense_model_name), 
                distance=models.Distance.COSINE
            )
        },  # size and distance are model dependent
        sparse_vectors_config={settings.content_sparse_vector_name: models.SparseVectorParams()},
    )

