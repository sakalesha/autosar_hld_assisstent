from fastapi import FastAPI
from config.settings import settings
from db.session import engine, Base
from src.ingestion.router import router as ingestion_router
from src.api.query_router import router as query_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0"
)

app.include_router(ingestion_router)
app.include_router(query_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
