from app.core.preflight import db_preflight, gpu_preflight

def check_health() -> dict[str, bool]:
    return {
        "db": db_preflight(),
        "gpu": gpu_preflight() is not None
    }
