from qdrant_client import QdrantClient

from .config import settings

app_qdrant = QdrantClient(url=settings.qdrant_url)

