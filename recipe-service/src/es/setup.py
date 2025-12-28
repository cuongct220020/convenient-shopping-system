from elasticsearch import Elasticsearch
from core.config import settings

def setup_indices():
    # Keep consistent with runtime client config
    client = Elasticsearch(
        hosts=[settings.ES_URL],
        basic_auth=(
            settings.ES_USERNAME,
            settings.ES_PASSWORD,
        ) if settings.ES_USERNAME else None,
    )
    create_ingredient_index(client)
    create_recipe_index(client)
    client.close()

def create_ingredient_index(client: Elasticsearch):
    body = {
        "mappings": {
            "properties": {
                "component_id": {"type": "keyword"},
                "type": {"type": "keyword"},
                "component_name": {"type": "text"},
                "unit": {"type": "keyword"},
            }
        }
    }
    if not client.indices.exists(index="ingredients"):
        client.indices.create(index="ingredients", body=body)

def create_recipe_index(client: Elasticsearch):
    body = {
        "mappings": {
            "properties": {
                "component_id": {"type": "keyword"},
                "type": {"type": "keyword"},
                "component_name": {"type": "text"},
                "component_list": {"type": "text"}
            }
        }
    }
    if not client.indices.exists(index="recipes"):
        client.indices.create(index="recipes", body=body)