from functools import lru_cache

from app.core.preflight import gpu_preflight
from app.core.settings import settings


def _device() -> str:
    info = gpu_preflight()
    return info["device"] if info else "cpu"


@lru_cache(maxsize=1)
def get_embedder():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(settings.EMBEDDING_MODEL, device=_device())


@lru_cache(maxsize=1)
def get_reranker():
    from sentence_transformers import CrossEncoder

    return CrossEncoder(
        settings.RERANKER_MODEL,
        device=_device(),
        max_length=int(settings.RERANK_MAX_LENGTH),
    )


def embed_query(query: str) -> list[float]:
    vec = get_embedder().encode(query, normalize_embeddings=True)
    return [float(x) for x in vec]