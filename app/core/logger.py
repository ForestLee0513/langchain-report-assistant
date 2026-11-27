import logging
import logging.handlers
import sys
from contextvars import ContextVar
from pathlib import Path

from app.core.settings import settings

# 요청 단위 추적용 ID (FastAPI 미들웨어에서 설정)
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="-")


class RequestIdFilter(logging.Filter):
    """모든 로그 레코드에 request_id 필드를 주입합니다."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_ctx.get()
        return True


class LoggerManager:
    """애플리케이션 로깅 설정을 관리합니다.

    - setup()은 여러 번 호출해도 한 번만 적용됩니다 (idempotent).
    - 설정은 root 로거에 하므로, 각 모듈은 get_logger(__name__)만 쓰면 됩니다.
    """

    FORMAT = (
        "%(asctime)s | %(levelname)-8s | %(request_id)s | "
        "%(name)s:%(lineno)d | %(message)s"
    )
    DATEFMT = "%Y-%m-%d %H:%M:%S"

    # 시끄러운 외부 라이브러리 로그 레벨
    NOISY_LOGGERS = {
        "httpx": logging.WARNING,
        "httpcore": logging.WARNING,
        "urllib3": logging.WARNING,
        "sqlalchemy.engine": logging.WARNING,  # SQL 로그가 필요하면 INFO
    }

    # uvicorn 로거는 root 핸들러로 통합
    UVICORN_LOGGERS = ("uvicorn", "uvicorn.error", "uvicorn.access")

    _configured: bool = False

    @classmethod
    def setup(
        cls,
        level: str | None = None,
        log_dir: str | None = None,
        to_file: bool | None = None,
    ) -> None:
        if cls._configured:
            return

        level = (level or settings.LOG_LEVEL).upper()
        log_dir = log_dir or settings.LOG_DIR
        to_file = settings.LOG_TO_FILE if to_file is None else to_file

        formatter = logging.Formatter(cls.FORMAT, datefmt=cls.DATEFMT)
        request_filter = RequestIdFilter()

        handlers: list[logging.Handler] = []

        # 콘솔
        console = logging.StreamHandler(sys.stdout)
        console.setFormatter(formatter)
        console.addFilter(request_filter)
        handlers.append(console)

        # 파일 (로테이션)
        if to_file:
            path = Path(log_dir)
            path.mkdir(parents=True, exist_ok=True)
            file_handler = logging.handlers.RotatingFileHandler(
                path / "app.log",
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,
                encoding="utf-8",
            )
            file_handler.setFormatter(formatter)
            file_handler.addFilter(request_filter)
            handlers.append(file_handler)

        # root 로거 설정 (기존 핸들러 제거 후 교체 → 중복 출력 방지)
        root = logging.getLogger()
        root.setLevel(level)
        for h in list(root.handlers):
            root.removeHandler(h)
        for h in handlers:
            root.addHandler(h)

        # 외부 라이브러리 레벨 조정
        for name, lvl in cls.NOISY_LOGGERS.items():
            logging.getLogger(name).setLevel(lvl)

        # uvicorn 로거를 root로 흘려보내 포맷 통일
        for name in cls.UVICORN_LOGGERS:
            lg = logging.getLogger(name)
            lg.handlers.clear()
            lg.propagate = True

        cls._configured = True
        logging.getLogger(__name__).info(
            "logging configured level=%s file=%s", level, to_file
        )

    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        return logging.getLogger(name)


def get_logger(name: str) -> logging.Logger:
    return LoggerManager.get_logger(name)