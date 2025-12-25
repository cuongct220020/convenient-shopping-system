from elasticsearch import Elasticsearch

def setup_indices():
    client = Elasticsearch([{'host': 'localhost', 'port': 9200}])
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
    if not client.indices.exists(index="ingredient"):
        client.indices.create(index="ingredient", body=body)

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
    if not client.indices.exists(index="recipe"):
        client.indices.create(index="recipe", body=body)