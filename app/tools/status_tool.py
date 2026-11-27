# app/tools/status_tool.py
from langchain_core.tools import tool

from app.core.logger import get_logger
from app.repositories.report import get_report_status
from app.tools._common import error_json

logger = get_logger(__name__)


@tool("lookup_status")
def lookup_status(report_id: int) -> str:
    """보고서 ID로 DB의 현재 인덱싱 상태와 Revision을 조회한다.

    인덱싱 상태, Revision, 최신 여부를 물을 때 사용한다. 값은 추측하지 않고 이 Tool 결과만 사용한다.
    """
    try:
        return get_report_status(report_id).model_dump_json()
    except Exception:
        logger.exception("lookup_status failed")
        return error_json("lookup_status failed")