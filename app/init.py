from qdrant_client.models import models
from app.client import app_qdrant


dense_vector_name = "dense"
sparse_vector_name = "sparse"
dense_model_name = "sentence-transformers/all-MiniLM-L6-v2"
sparse_model_name = "prithivida/Splade_PP_en_v1"

def create_collections_if_not_exists():
    """
    Create the 'startups' collection if it does not already exist.
    """
    app_qdrant.create_collection(
        collection_name="posts",
        vectors_config={
            dense_vector_name: models.VectorParams(
                size=app_qdrant.get_embedding_size(dense_model_name), 
                distance=models.Distance.COSINE
            )
        },  # size and distance are model dependent
        sparse_vectors_config={sparse_vector_name: models.SparseVectorParams()},
    )

