from pydantic import BaseModel


class RagHit(BaseModel):
    report_id: int
    title: str | None = None
    score: float
    snippet: str


class RagSearchResult(BaseModel):
    hits: list[RagHit]