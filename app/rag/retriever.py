# app/rag/retriever.py
from sqlalchemy import select, text

from app.db.session import  get_session_factory
from app.core.settings import settings
from app.rag.models import embed_query, get_reranker
from app.schemas.rag import RagHit, RagSearchResult
from app.models.report import ReportReadView, ReportEmbed


def _fetch_candidates(query: str, report_id: int | None) -> list[dict]:
    stmt = (
        select(
            ReportReadView.report_id,
            ReportReadView.title,
            ReportReadView.content,
            ReportReadView.category_code,
            ReportReadView.revision,
        )
        .join(ReportEmbed, ReportReadView.report_id == ReportEmbed.report_id)
        .order_by(ReportEmbed.embedding.cosine_distance(embed_query(query)))
        .limit(int(settings.RETRIEVE_K))
    )

    if report_id is not None:
        stmt = stmt.where(ReportEmbed.report_id == report_id)

    with get_session_factory()() as session:
        session.execute(
            text(f"SET LOCAL statement_timeout = {int(settings.DB_TIMEOUT_MS)}")
        )
        rows = session.execute(stmt).mappings().all()

    return [dict(r) for r in rows]


def _rerank(query: str, rows: list[dict]) -> list[tuple[dict, float]]:
    pairs = [(query, r["content"]) for r in rows]
    scores = get_reranker().predict(pairs, batch_size=int(settings.RERANK_BATCH_SIZE))
    return sorted(zip(rows, map(float, scores)), key=lambda x: x[1], reverse=True)


def search(query: str, report_id: int | None = None) -> RagSearchResult:
    """벡터 검색 → 리랭크 → 임계값 필터 → 상위 CONTEXT_K개. 근거가 없으면 hits=[]."""
    rows = _fetch_candidates(query, report_id)
    if not rows:
        return RagSearchResult(hits=[])

    min_score = float(getattr(settings, "RERANK_MIN_SCORE", 0.3))
    context_k = int(settings.CONTEXT_K)
    per_hit_chars = max(int(settings.CONTEXT_CHARS) // max(context_k, 1), 200)

    hits = [
        RagHit(
            report_id=int(r["report_id"]),
            title=r["title"],
            score=round(score, 4),
            snippet=r["content"][:per_hit_chars],
        )
        for r, score in _rerank(query, rows)
        if score >= min_score
    ][:context_k]

    return RagSearchResult(hits=hits)