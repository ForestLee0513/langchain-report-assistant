from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.report import ReportStatus


class ModelAnswer(BaseModel):
    """모델이 생성하는 구조화 출력 (검증 전)."""

    status: Literal["answered", "insufficient_evidence"] = Field(
        description="Tool 결과로 답할 수 있으면 answered, 근거가 없으면 insufficient_evidence"
    )
    answer: str = Field(description="한국어 답변. Tool 결과에 있는 내용만 사용")
    cited_report_ids: list[int] = Field(
        default_factory=list,
        description="근거로 사용한 보고서 ID. Tool 결과에 실제로 나온 ID만 허용",
    )


class Citation(BaseModel):
    report_id: int
    title: str | None = None
    snippet: str


class AgentResult(BaseModel):
    """API 최종 응답. 출처/상태/Tool 이력은 코드가 Tool 실행 기록에서 채운다."""

    status: Literal["answered", "insufficient_evidence"]
    answer: str
    citations: list[Citation] = []
    index_statuses: list[ReportStatus] = []
    tools_used: list[str] = []