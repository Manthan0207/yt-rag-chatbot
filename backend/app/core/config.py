from functools import lru_cache 
from pydantic import BaseModel 
import os 

class Settings(BaseModel) :
    project_name : str = "yt-rag-chatbot"
    api_v1_prefix : str = "/api/v1"
    
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    secret_key : str = os.getenv("SECRET_KEY" , "sample")
    algorithm : str = "SHA256"
    access_token_expire_minutes : int= int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080")) #7 days 
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    pinecone_api_key: str = os.getenv("PINECONE_API_KEY", "")
    pinecone_index_name: str = os.getenv("PINECONE_INDEX_NAME", "youtube-ai-chatbot")
    pinecone_namespace: str = os.getenv("PINECONE_NAMESPACE", "shared")

    cors_origins: list[str] = ["http://localhost:3000"]
    
@lru_cache
def get_settings() -> Settings : 
    return Settings()

settings = get_settings()
