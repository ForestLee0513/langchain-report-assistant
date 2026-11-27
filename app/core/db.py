from sqlalchemy import create_engine, Engine

from app.core.settings import settings
from app.core.logger import get_logger


logger = get_logger(__name__)


def get_db() -> Engine:
    try:
        db = create_engine(settings.DATABASE_URL)
        return db
    except Exception as exc:
        logger.exception(exc)
        return None


db = get_db()