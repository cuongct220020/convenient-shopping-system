import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:9002"

# Headers must simulate Kong injection
HEADERS = {
    "X-User-ID": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "X-User-Role": "admin",
    "X-User-Email": "admin@example.com",
    "X-JTI": "test-jti-12345",
    "X-IAT": str(int(time.time())),
    "X-EXP": str(int(time.time()) + 3600)
}

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'
BLUE = '\033[94m'

def print_success(msg):
    print(f"{GREEN}[PASS] {msg}{RESET}")

def print_error(msg):
    print(f"{RED}[FAIL] {msg}{RESET}")

def print_info(msg):
    print(f"{BLUE}[INFO] {msg}{RESET}")

# Store created IDs
context = {
    "ingredient_ids": {},
    "recipe_ids": {}
}

def test_create_ingredients():
    print_info("\n--- 1. CREATE - Ingredients ---")
    ingredients = [
        {"type": "countable_ingredient", "component_name": "Cà chua", "category": "Rau củ", "c_measurement_unit": "quả", "estimated_shelf_life": 7, "protein": 0.9, "fat": 0.2, "carb": 3.9, "fiber": 1.2, "calories": 18, "estimated_price": 5000},
        {"type": "countable_ingredient", "component_name": "Thịt lợn", "category": "Thịt tươi", "c_measurement_unit": "miếng", "estimated_shelf_life": 3, "protein": 27.0, "fat": 14.0, "carb": 0.0, "fiber": 0.0, "calories": 242, "estimated_price": 150000},
        {"type": "countable_ingredient", "component_name": "Tôm", "category": "Hải sản và cá viên", "c_measurement_unit": "con", "estimated_shelf_life": 2, "protein": 24.0, "fat": 0.3, "carb": 0.2, "fiber": 0.0, "calories": 99, "estimated_price": 200000},
        {"type": "countable_ingredient", "component_name": "Chuối", "category": "Trái cây tươi", "c_measurement_unit": "quả", "estimated_shelf_life": 5, "protein": 1.1, "fat": 0.3, "carb": 23.0, "fiber": 2.6, "calories": 89, "estimated_price": 15000},
        {"type": "countable_ingredient", "component_name": "Tỏi", "category": "Gia vị", "c_measurement_unit": "củ", "estimated_shelf_life": 30, "protein": 6.4, "fat": 0.5, "carb": 33.0, "fiber": 2.1, "calories": 149, "estimated_price": 20000},
        {"type": "uncountable_ingredient", "component_name": "Sữa tươi", "category": "Sữa", "uc_measurement_unit": "ML", "estimated_shelf_life": 7, "protein": 3.3, "fat": 3.6, "carb": 4.8, "fiber": 0.0, "calories": 61, "estimated_price": 25000},
        {"type": "uncountable_ingredient", "component_name": "Gạo trắng", "category": "Lương thực", "uc_measurement_unit": "G", "estimated_shelf_life": 365, "protein": 7.1, "fat": 0.7, "carb": 77.0, "fiber": 0.4, "calories": 365, "estimated_price": 30000},
        {"type": "uncountable_ingredient", "component_name": "Dầu ăn", "category": "Gia vị", "uc_measurement_unit": "ML", "estimated_shelf_life": 180, "protein": 0.0, "fat": 100.0, "carb": 0.0, "fiber": 0.0, "calories": 884, "estimated_price": 50000},
        {"type": "countable_ingredient", "component_name": "Bánh mì", "category": "Bánh ngọt", "c_measurement_unit": "củ", "estimated_shelf_life": 2, "protein": 9.0, "fat": 3.2, "carb": 49.0, "fiber": 2.7, "calories": 265, "estimated_price": 10000},
        {"type": "countable_ingredient", "component_name": "Trứng gà", "category": "Khác", "c_measurement_unit": "quả", "estimated_shelf_life": 30, "protein": 13.0, "fat": 11.0, "carb": 1.1, "fiber": 0.0, "calories": 155, "estimated_price": 3000}
    ]

    for ing in ingredients:
        try:
            resp = requests.post(f"{BASE_URL}/v2/ingredients/", json=ing, headers=HEADERS)
            if resp.status_code == 201:
                data = resp.json()
                print_success(f"Created {data['component_name']} (ID: {data['component_id']})")
                context["ingredient_ids"][data["component_name"]] = data["component_id"]
            elif resp.status_code == 400 and "already exists" in resp.text:
                print_info(f"{ing['component_name']} might already exist, trying to search...")
                # Try to search for it to get ID
                search_resp = requests.get(f"{BASE_URL}/v2/ingredients/search", params={"keyword": ing['component_name']}, headers=HEADERS)
                if search_resp.status_code == 200:
                    results = search_resp.json()['data']
                    for r in results:
                         if r['component_name'] == ing['component_name']:
                             context["ingredient_ids"][r["component_name"]] = r["component_id"]
                             print_success(f"Found existing {r['component_name']} (ID: {r['component_id']})")
                             break
            else:
                print_error(f"Failed to create {ing['component_name']}: {resp.status_code} - {resp.text}")
        except Exception as e:
            print_error(f"Exception creating {ing['component_name']}: {e}")

def test_get_search_filter_ingredients():
    print_info("\n--- 2. GET/SEARCH/FILTER - Ingredients ---")
    
    # Get by ID
    if context["ingredient_ids"]:
        first_name = list(context["ingredient_ids"].keys())[0]
        first_id = context["ingredient_ids"][first_name]
        resp = requests.get(f"{BASE_URL}/v2/ingredients/{first_id}", headers=HEADERS)
        if resp.status_code == 200:
            print_success(f"Get Ingredient {first_id}: OK")
        else:
            print_error(f"Get Ingredient {first_id}: {resp.status_code} - {resp.text}")

    # Search
    resp = requests.get(f"{BASE_URL}/v2/ingredients/search", params={"keyword": "thịt"}, headers=HEADERS)
    if resp.status_code == 200:
        data = resp.json()['data']
        if len(data) > 0:
             print_success(f"Search 'thịt': Found {len(data)} items")
        else:
             print_info("Search 'thịt': Found 0 items")
    else:
        print_error(f"Search 'thịt' failed: {resp.text}")

    # Filter
    resp = requests.get(f"{BASE_URL}/v2/ingredients/filter", params={"category": "Rau củ"}, headers=HEADERS)
    if resp.status_code == 200:
        data = resp.json()['data']
        if len(data) > 0:
            print_success(f"Filter 'Rau củ': Found {len(data)} items")
        else:
            print_info("Filter 'Rau củ': Found 0 items")
    else:
        print_error(f"Filter 'Rau củ' failed: {resp.text}")

def test_create_recipes():
    print_info("\n--- 3. CREATE - Recipes ---")
    
    # Helper to get ID
    def get_id(name):
        return context["ingredient_ids"].get(name)

    if not get_id("Cà chua"):
        print_error("Missing Cà chua ID, skipping recipe creation")
        return

    recipes = [
        {
            "component_name": "Salad cà chua",
            "level": "Dễ",
            "default_servings": 2,
            "prep_time": 10,
            "instructions": ["Rửa sạch", "Trộn đều"],
            "keywords": ["salad", "cà chua"],
            "component_list": [
                {"component_id": get_id("Cà chua"), "quantity": 4},
                {"component_id": get_id("Tỏi"), "quantity": 2},
                {"component_id": get_id("Dầu ăn"), "quantity": 15}
            ]
        },
        {
            "component_name": "Thịt lợn kho tàu",
            "level": "Trung bình",
            "default_servings": 4,
            "prep_time": 15,
            "cook_time": 45,
            "instructions": ["Ướp thịt", "Kho"],
            "keywords": ["thịt lợn", "kho"],
            "component_list": [
                {"component_id": get_id("Thịt lợn"), "quantity": 4},
                {"component_id": get_id("Tỏi"), "quantity": 3},
                {"component_id": get_id("Dầu ăn"), "quantity": 20}
            ]
        },
        {
            "component_name": "Tôm rang me",
            "level": "Trung bình",
            "default_servings": 3,
            "prep_time": 20,
            "cook_time": 15,
            "instructions": ["Rang tôm", "Thêm me"],
            "keywords": ["tôm", "rang me"],
            "component_list": [
                {"component_id": get_id("Tôm"), "quantity": 10},
                {"component_id": get_id("Tỏi"), "quantity": 2},
                {"component_id": get_id("Dầu ăn"), "quantity": 25}
            ]
        }
    ]

    for r in recipes:
        # Check if IDs are valid
        if any(c["component_id"] is None for c in r["component_list"]):
            print_error(f"Missing ingredient ID for {r['component_name']}")
            continue

        resp = requests.post(f"{BASE_URL}/v2/recipes/", json=r, headers=HEADERS)
        if resp.status_code == 201:
            data = resp.json()
            print_success(f"Created {data['component_name']} (ID: {data['component_id']})")
            context["recipe_ids"][data["component_name"]] = data["component_id"]
        elif resp.status_code == 400 and ("unique constraint" in resp.text.lower() or "uniqueviolation" in resp.text.lower()):
             # Try search
             print_info(f"Recipe {r['component_name']} might exist, searching...")
             search_resp = requests.get(f"{BASE_URL}/v2/recipes/search", params={"keyword": r['component_name']}, headers=HEADERS)
             if search_resp.status_code == 200:
                 for res in search_resp.json()['data']:
                     if res['component_name'] == r['component_name']:
                         context["recipe_ids"][res['component_name']] = res['component_id']
                         print_success(f"Found existing {res['component_name']} (ID: {res['component_id']})")
        else:
             print_error(f"Failed to create {r['component_name']}: {resp.status_code} - {resp.text}")

    # Nested Recipes
    # Cơm chiên (chứa Thịt lợn kho tàu)
    thit_kho_id = context["recipe_ids"].get("Thịt lợn kho tàu")
    if thit_kho_id:
        com_chien = {
            "component_name": "Cơm chiên",
            "level": "Khó",
            "default_servings": 4,
            "prep_time": 30,
            "cook_time": 20,
            "instructions": ["Chiên cơm", "Thêm thịt kho"],
            "keywords": ["cơm chiên"],
            "component_list": [
                {"component_id": get_id("Gạo trắng"), "quantity": 400},
                {"component_id": thit_kho_id, "quantity": 1},
                {"component_id": get_id("Trứng gà"), "quantity": 2},
                {"component_id": get_id("Dầu ăn"), "quantity": 30}
            ]
        }
        resp = requests.post(f"{BASE_URL}/v2/recipes/", json=com_chien, headers=HEADERS)
        if resp.status_code == 201:
            data = resp.json()
            print_success(f"Created Nested: {data['component_name']} (ID: {data['component_id']})")
            context["recipe_ids"][data["component_name"]] = data["component_id"]
        elif resp.status_code == 400 and ("unique constraint" in resp.text.lower() or "uniqueviolation" in resp.text.lower()):
             print_info(f"Recipe Cơm chiên might exist, searching...")
             search_resp = requests.get(f"{BASE_URL}/v2/recipes/search", params={"keyword": "Cơm chiên"}, headers=HEADERS)
             if search_resp.status_code == 200:
                 for res in search_resp.json()['data']:
                     if res['component_name'] == "Cơm chiên":
                         context["recipe_ids"]["Cơm chiên"] = res['component_id']
                         print_success(f"Found existing Cơm chiên (ID: {res['component_id']})")
        else:
            print_error(f"Failed to create Cơm chiên: {resp.status_code} - {resp.text}")

def test_get_search_recipes():
    print_info("\n--- 4. GET/SEARCH - Recipes ---")
    
    if not context["recipe_ids"]:
        return

    # Get Detail
    r_id = list(context["recipe_ids"].values())[0]
    resp = requests.get(f"{BASE_URL}/v2/recipes/{r_id}", headers=HEADERS)
    if resp.status_code == 200:
        print_success(f"Get Recipe {r_id}: OK")
    else:
        print_error(f"Get Recipe {r_id} failed: {resp.text}")

    # Get Detailed (Nested)
    com_chien_id = context["recipe_ids"].get("Cơm chiên")
    if com_chien_id:
        resp = requests.get(f"{BASE_URL}/v2/recipes/detailed/{com_chien_id}", headers=HEADERS)
        if resp.status_code == 200:
            print_success(f"Get Detailed Recipe {com_chien_id}: OK")
            # Verify nested structure
            data = resp.json()
            has_nested = any(item['component']['type'] == 'recipe' for item in data['component_list'])
            if has_nested:
                print_success("Nested structure verified")
            else:
                print_error("Nested structure missing")
        else:
            print_error(f"Get Detailed Recipe failed: {resp.text}")

    # Search
    resp = requests.get(f"{BASE_URL}/v2/recipes/search", params={"keyword": "thịt"}, headers=HEADERS)
    if resp.status_code == 200:
        print_success(f"Search Recipes 'thịt': Found {len(resp.json()['data'])} items")

def test_flattened():
    print_info("\n--- 5. FLATTENED - Recipes ---")
    salad_id = context["recipe_ids"].get("Salad cà chua")
    thit_id = context["recipe_ids"].get("Thịt lợn kho tàu")
    
    if salad_id and thit_id:
        payload = [
            {"recipe_id": salad_id, "quantity": 2},
            {"recipe_id": thit_id, "quantity": 1}
        ]
        resp = requests.post(f"{BASE_URL}/v2/recipes/flattened", params={"check_existence": "false"}, json=payload, headers=HEADERS)
        if resp.status_code == 200:
            print_success("Flattened recipes: OK")
            # print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
        else:
            print_error(f"Flattened failed: {resp.status_code} - {resp.text}")

def test_update():
    print_info("\n--- 6. UPDATE - Ingredients/Recipes ---")
    
    # Update Ingredient
    ing_name = "Cà chua"
    ing_id = context["ingredient_ids"].get(ing_name)
    if ing_id:
        # Update name
        new_name = f"Cà chua update {int(time.time())}"
        resp = requests.put(f"{BASE_URL}/v2/ingredients/{ing_id}", json={"type": "countable_ingredient", "component_name": new_name}, headers=HEADERS)
        if resp.status_code == 200:
            print_success(f"Update Ingredient {ing_id} to {new_name}: OK")
            # Revert
            requests.put(f"{BASE_URL}/v2/ingredients/{ing_id}", json={"type": "countable_ingredient", "component_name": ing_name}, headers=HEADERS)
        else:
            print_error(f"Update Ingredient failed: {resp.text}")

    # Update Recipe
    rec_name = "Salad cà chua"
    rec_id = context["recipe_ids"].get(rec_name)
    if rec_id:
        resp = requests.put(f"{BASE_URL}/v2/recipes/{rec_id}", json={"default_servings": 5}, headers=HEADERS)
        if resp.status_code == 200 and resp.json()['default_servings'] == 5:
            print_success(f"Update Recipe {rec_id} servings to 5: OK")
        else:
            print_error(f"Update Recipe failed: {resp.text}")

if __name__ == "__main__":
    try:
        test_create_ingredients()
        test_get_search_filter_ingredients()
        test_create_recipes()
        test_get_search_recipes()
        test_flattened()
        test_update()
    except Exception as e:
        print_error(f"Test crashed: {e}")