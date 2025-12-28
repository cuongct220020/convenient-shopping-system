from elasticsearch import AsyncElasticsearch
from core.config import settings

_es: AsyncElasticsearch | None = None

async def init_es():
    global _es
    _es = AsyncElasticsearch(
        hosts=[settings.ES_URL],
        basic_auth=(
            settings.ES_USERNAME,
            settings.ES_PASSWORD,
        ) if settings.ES_USERNAME else None,
    )

async def close_es():
    if _es:
        await _es.close()

def get_es():
    if _es is None:
        raise RuntimeError("ElasticSearch client is not initialized")
    return _es
