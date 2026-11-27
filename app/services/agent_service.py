# app/services/agent_service.py
from langchain_core.messages import ToolMessage
from pydantic import ValidationError

from app.agent import get_agent
from app.core.logger import get_logger
from app.core.settings import settings
from app.schemas.agent import AgentResult, Citation, ModelAnswer
from app.schemas.rag import RagSearchResult
from app.schemas.report import ReportStatus
from app.tools import lookup_status, rag_search

logger = get_logger(__name__)

INSUFFICIENT_MESSAGE = "제공된 DB에서 이 질문을 뒷받침할 근거를 찾지 못했습니다."


def _collect_evidence(
    messages: list,
) -> tuple[dict[int, Citation], dict[int, ReportStatus], list[str]]:
    """ToolMessage에서 실제 실행된 Tool과 그 결과만 추출한다."""
    citations: dict[int, Citation] = {}
    statuses: dict[int, ReportStatus] = {}
    used: set[str] = set()

    for m in messages:
        if not isinstance(m, ToolMessage) or getattr(m, "status", "success") == "error":
            continue
        if not isinstance(m.content, str):
            continue

        try:
            if m.name == rag_search.name:
                result = RagSearchResult.model_validate_json(m.content)
                used.add(m.name)
                for h in result.hits:
                    citations.setdefault(
                        h.report_id,
                        Citation(report_id=h.report_id, title=h.title, snippet=h.snippet),
                    )
            elif m.name == lookup_status.name:
                status = ReportStatus.model_validate_json(m.content)
                used.add(m.name)
                if status.found:
                    statuses[status.report_id] = status
        except ValidationError:
            continue  # error JSON 등 스키마에 맞지 않는 결과는 증거로 인정하지 않음

    return citations, statuses, sorted(used)


def run_agent(question: str) -> AgentResult:
    try:
        out = get_agent().invoke(
            {"messages": [{"role": "user", "content": question}]},
            config={"recursion_limit": int(settings.MAX_MODEL_CALLS) * 2 + 5},
        )
    except Exception:
        logger.exception("agent invoke failed")
        return AgentResult(status="insufficient_evidence", answer=INSUFFICIENT_MESSAGE)

    citations, statuses, used = _collect_evidence(out.get("messages", []))
    parsed: ModelAnswer | None = out.get("structured_response")

    if parsed is None:  # 호출 제한 초과 등
        logger.warning("no structured_response (limit reached?)")
        return AgentResult(
            status="insufficient_evidence", answer=INSUFFICIENT_MESSAGE, tools_used=used
        )

    real_ids = set(citations) | set(statuses)
    valid_ids = [i for i in parsed.cited_report_ids if i in real_ids]
    fabricated = [i for i in parsed.cited_report_ids if i not in real_ids]
    if fabricated:
        logger.warning("dropped fabricated report ids: %s", fabricated)

    if parsed.status == "insufficient_evidence" or (not valid_ids and not statuses):
        keep_answer = parsed.status == "insufficient_evidence" and not fabricated
        return AgentResult(
            status="insufficient_evidence",
            answer=parsed.answer if keep_answer else INSUFFICIENT_MESSAGE,
            tools_used=used,
        )

    return AgentResult(
        status="answered",
        answer=parsed.answer,
        citations=[citations[i] for i in valid_ids if i in citations],
        index_statuses=list(statuses.values()),
        tools_used=used,
    )