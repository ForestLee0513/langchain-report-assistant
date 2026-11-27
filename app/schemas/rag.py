from pydantic import BaseModel


class RagHit(BaseModel):
    report_id: int
    title: str | None = None
    chunk_index: int
    score: float
    snippet: str


class RagSearchResult(BaseModel):
    hits: list[RagHit]