import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import health, schemas, generate, execute

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("text-to-sql-backend")

app = FastAPI(
    title="Text-to-SQL AI API",
    description="Backend API for fine-tuned Text-to-SQL conversion, validation, and self-correction.",
    version="0.1.0"
)

# CORS configuration
# Allowing frontend connections dynamically based on config
origins = [origin.strip().rstrip("/") for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]
app.add_middleware(

    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register routers
app.include_router(health.router, tags=["Health"])
app.include_router(schemas.router, tags=["Schemas"])
app.include_router(generate.router, tags=["Generate"])
app.include_router(execute.router, tags=["Execute"])

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Text-to-SQL AI backend server. Please view docs at /docs."
    }

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting server in {settings.APP_ENV} env...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
