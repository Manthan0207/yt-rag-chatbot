from pinecone import Pinecone
from app.core.config import settings

pc = Pinecone(api_key=settings.pinecone_api_key)


def get_index():
    return pc.Index(settings.pinecone_index_name)