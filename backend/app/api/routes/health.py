from fastapi import APIRouter
from app.core.config import settings
from app.models.responses import HealthResponse
from app.db.duckdb_client import get_duckdb_conn

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
def health_check():
    # Check if DuckDB database exists and is readable
    duckdb_ready = False
    try:
        with get_duckdb_conn(read_only=True) as conn:
            conn.execute("SELECT 1")
            duckdb_ready = True
    except Exception:
        pass

    # Model is loaded if it's cached or if we are in mock mode
    from app.llm.model_loader import _model
    model_loaded = settings.MOCK_MODEL or (_model is not None)

    return HealthResponse(
        status="ok" if (duckdb_ready and model_loaded) else "degraded",
        model_loaded=model_loaded,
        duckdb_ready=duckdb_ready,
        version="0.1.0"
    )
