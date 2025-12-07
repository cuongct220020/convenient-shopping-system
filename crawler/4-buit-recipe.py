import json
from unidecode import unidecode

# Load files
with open('/home/gpus/hachi/convenient-shopping-system/crawler/data/ingredient_v7.json', 'r', encoding='utf-8') as f:
    ingredients = json.load(f)

with open('/mnt/disk1/hachi/crawler/data/recipes_detail.json', 'r', encoding='utf-8') as f:
    recipes = json.load(f)

# Tạo mapping dictionary: name_vi -> {id, category, name_en}
ingredient_map = {}
for ing in ingredients:
    name = ing['name'].lower().strip()
    unit = ing['unit_recipe'].lower().strip()
    ingredient_map[name+unit] = {
        'name': ing['name'],
        'quantity': ing.get('quantity', 1),
        'unit': ing['unit']
    }

# Normalize Vietnamese text
def normalize(text):
    return unidecode(text).lower()

# Process recipes
dishes = []
seen_dishes = set()  # Track các món đã thêm

for idx, recipe in enumerate(recipes, start=1):
    print(idx)
    try:
        dish_name = recipe['dish_name'].lower().strip()
        
        # Skip nếu món này đã có
        if dish_name in seen_dishes:
            continue
        
        seen_dishes.add(dish_name)
        
        dish = {
            "id": f"dish{str(len(dishes) + 1).zfill(4)}",
            "name": recipe['dish_name'],
            "category": normalize(recipe.get('category', '')),
            "ingredients": [],
            "img_url": recipe['img_url'],
            "pre_time": recipe['times']['Chuẩn bị'],
            "cook_time": recipe['times']['Chế biến'],
            "level": recipe['level'],
            "servings": recipe['servings'],
            "instructions": recipe['instructions']
        }
        
        # Tính threshold cho 30% đầu
        total_ingredients = len(recipe['ingredients'])
        critical_threshold = int(total_ingredients * 0.3)
        normal_threshold = int(total_ingredients * 0.7)
        
        for ing_idx, ing in enumerate(recipe['ingredients']):
            ing_name = ing['name'].lower().strip()
            unit = ing['unit'].lower().strip()
            ingredient_data = ingredient_map.get(ing_name+unit, None)
            if not ingredient_data:
                continue
            # Xác định importance: 30% đầu là critical, còn lại là normal
            importance = 3 if ing_idx < critical_threshold else 2 if ing_idx < normal_threshold else 1

            dish['ingredients'].append({
                "name": ingredient_data['name'],
                "quantity": ing.get('quantity', 0)*ingredient_data['quantity'],
                "unit": ingredient_data['unit'],
                "unit_recipe": ing.get('unit', '')
            })
        
        dishes.append(dish)
    
    except:
        continue

# Save output
with open('/mnt/disk1/hachi/crawler/data/recipe_v2.json', 'w', encoding='utf-8') as f:
    json.dump(dishes, f, ensure_ascii=False, indent=2)

print(f"✅ Đã tạo {len(dishes)} món ăn trong dish_knowledge_base.json")
