from fastapi import FastAPI
from config.settings import settings
from db.session import engine, Base
from src.ingestion.router import router as ingestion_router

# Ensure all database tables defined in our models are created when the app starts.
# In a production environment, this should ideally be handled by a migration tool like Alembic.
Base.metadata.create_all(bind=engine)

# Initialize the core FastAPI application instance
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0"
)

# Register the ingestion module's routes under the main application
app.include_router(ingestion_router)

@app.get("/health")
def health_check():
    """
    Basic health check endpoint to verify the service is running.
    Useful for container orchestration (Docker/Kubernetes) or load balancers.
    """
    return {"status": "ok"}
