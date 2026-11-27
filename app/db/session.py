"""SQLAlchemy DB 연결과 세션 수명 관리. HTTP 요청당 세션을 하나 사용합니다."""
from functools import lru_cache
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.settings import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def get_engine():
    if not settings.DATABASE_URL or 'CHANGE_ME' in settings.DATABASE_URL:
        logger.exception('DB is unavailable. Please check PostgreSQL info on DATABASE_URL (.env)')
    return create_engine(settings.DATABASE_URL, pool_pre_ping=True, pool_size=5, max_overflow=5)


@lru_cache(maxsize=1)
def get_session_factory():
    return sessionmaker(bind=get_engine(), expire_on_commit=False, autoflush=False)


def get_db():
    # Router에서 Depends(get_db)로 사용. 서비스에서 commit 또는 rollback합니다.
    with get_session_factory()() as db:
        yield db