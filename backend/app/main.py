from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.database import Base, engine
from app.routers.auth import router as auth_router
from app.routers.threads import router as threads_router
from app.routers.videos import router as videos_router


Base.metadata.create_all(bind=engine)
app = FastAPI(title=settings.project_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(threads_router, prefix="/threads", tags=["threads"])
app.include_router(videos_router, prefix="/videos", tags=["videos"])

@app.get("/health")
def health():
    return {"status": "ok"}