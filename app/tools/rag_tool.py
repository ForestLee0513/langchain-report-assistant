# app/tools/rag_tool.py
from langchain_core.tools import tool

from app.core.logger import get_logger
from app.rag.retriever import search
from app.tools._common import error_json

logger = get_logger(__name__)


@tool("rag_search")
def rag_search(query: str, report_id: int | None = None) -> str:
    """보고서 본문을 의미 검색해 근거 문단과 보고서 ID를 반환한다.

    보고서의 내용·주제·결과를 찾거나 설명할 때 사용한다.
    특정 보고서 번호가 질문에 있으면 report_id로 검색 범위를 제한한다.
    hits가 비어 있으면 DB에 관련 근거가 없다는 뜻이다.
    """
    try:
        return search(query, report_id).model_dump_json()
    except Exception:
        logger.exception("rag_search failed")
        return error_json("rag_search failed")