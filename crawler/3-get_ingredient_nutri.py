import requests
from requests_oauthlib import OAuth1
import time
import json
import os
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()
CONSUMER_KEY = os.getenv('CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('CONSUMER_SECRET')
BASE_URL = "https://platform.fatsecret.com/rest/server.api"

def search_food(query):
    auth = OAuth1(CONSUMER_KEY, CONSUMER_SECRET)
    params = {
        "method": "foods.search",
        "search_expression": query,
        "format": "json"
    }

    res = requests.get(BASE_URL, params=params, auth=auth).json()
    # Nếu có lỗi từ API
    if "error" in res:
        raise Exception(res["error"]["message"])
    # Không có kết quả
    if "foods" not in res or "food" not in res["foods"]:
        raise Exception("Missing field 'food' in response")

    food = res["foods"]["food"][0]
    return food['food_description']

def get_input(input_file):
    if input_file.endswith('.json'):
        with open(input_file, 'r', encoding='utf-8') as fin:
            ingredients = json.load(fin)
    elif input_file.endswith('.txt'):
        ingredients = []
        with open(input_file, 'r', encoding='utf-8') as fin:
            for line in fin:
                id, name, _ = line.strip().split('\t')
                ingre = {
                    'id': id,
                    'name_en': name
                }
                ingredients.append(ingre)
    else:
        return None
    return ingredients
def get_nutrition(food_id):
    if food_id is None:
        return None

    auth = OAuth1(CONSUMER_KEY, CONSUMER_SECRET)
    params = {
        "method": "food.get.v2",
        "food_id": food_id,
        "format": "json"
    }

    res = requests.get(BASE_URL, params=params, auth=auth).json()

    # Nếu có lỗi từ API
    if "error" in res:
        raise Exception(res["error"]["message"])

    # Nếu không có food object
    if "food" not in res:
        raise Exception("Missing field 'food' in response")

    food = res["food"]

    # Trường servings có thể khác dạng: object hoặc list
    servings = food.get("servings", {})
    serving = servings.get("serving")

    # serving có thể là dict hoặc list
    if isinstance(serving, list):
        serving = serving[0]

    if not isinstance(serving, dict):
        raise Exception(f'Invalid serving format: {serving}')
    return {
        "protein": serving.get("protein"),
        "fat": serving.get("fat"),
        "fiber": serving.get("fiber"),
        "carb": serving.get("carbohydrate"),
        "calo": serving.get("calories"),
        "unit": serving.get('serving_description')
    }

def main():
    #input_file = './data/ingredient_v1.json'
    input_file = './data/tmp/pre_error.txt'
    nutri_file = '/mnt/disk1/hachi/crawler/data/tmp/ingredient_v1_nutri.jsonl'   # JSON Lines
    error_file = '/mnt/disk1/hachi/crawler/data/tmp/error.txt'
    print(input_file)
    os.makedirs(os.path.dirname(nutri_file), exist_ok=True)
    BATCH_SIZE = 50   # mỗi 100 nguyên liệu thì flush xuống file

    ingredients = get_input(input_file)

    batch_nutri = []
    batch_error = []

    for ingre in tqdm(ingredients):
        try:
            time.sleep(0.5)
            item = ingre['name_en']
            food = search_food(item)

            batch_nutri.append({
                "id": ingre['id'],
                "name": ingre['name_en'],
                "nutrition": food
            })

        except Exception as e:
            batch_error.append(f"{ingre['id']}\t{ingre['name_en']}\t{str(e)}")

        # ------------------------------------------------
        # GHI FILE THEO BATCH
        # ------------------------------------------------
        if len(batch_nutri) >= BATCH_SIZE:
            with open(nutri_file, "a", encoding='utf-8') as f:
                for row in batch_nutri:
                    f.write(json.dumps(row, ensure_ascii=False) + "\n")
            batch_nutri = []   # clear batch

        if len(batch_error) >= 20:
            with open(error_file, "a", encoding='utf-8') as f:
                for line in batch_error:
                    f.write(line + "\n")
            batch_error = []   # clear batch

    # ------------------------------------------------
    # GHI NỐT PHẦN CÒN LẠI
    # ------------------------------------------------
    if batch_nutri:
        with open(nutri_file, "a", encoding='utf-8') as f:
            for row in batch_nutri:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")

    if batch_error:
        with open(error_file, "a", encoding='utf-8') as f:
            for line in batch_error:
                f.write(line + "\n")

    print("\n DONE!")
    print(f"✔ Saved nutrition batch-wise → {nutri_file}")
    print(f"✔ Saved errors → {error_file}")


if __name__ == "__main__":
    main()