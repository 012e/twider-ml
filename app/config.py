from pydantic import BaseModel


class Settings(BaseModel):
    """Application settings with environment variable support."""
    
    # Qdrant settings
    qdrant_url: str = "http://localhost:6333"
    
    # NATS settings
    nats_url: str = "localhost"
    
    # Vector settings
    content_dense_vector_name: str = "dense"
    content_sparse_vector_name: str = "sparse"
    content_dense_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    content_sparse_model_name: str = "prithivida/Splade_PP_en_v1"
    
    # Collection settings
    posts_collection_name: str = "posts"
    
    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "info"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
