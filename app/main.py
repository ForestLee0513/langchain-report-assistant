from pathlib import Path

from fastapi import FastAPI, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")

from app.core.settings import settings
from app.core.runtime import check_health
from app.core.logger import LoggerManager, get_logger
from app.api.agent import router as agent_router


LoggerManager.setup()
logger = get_logger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)


app.include_router(agent_router)


@app.get("/health", tags=["Health"])
def health():
    try:
        health_states = check_health() 
    except Exception:
        logger.exception("health check failed")
        return JSONResponse(
            status_code=503,
            content={"status": "error", "checks": {}},
        )

    is_ok = all(health_states.values())

    return JSONResponse(
        status_code=200 if is_ok else 503,
        content={
            "status": "ok" if is_ok else "error",
            "checks": health_states,
        },
    )