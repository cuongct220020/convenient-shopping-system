import sqlite3
import json

# Kết nối database
db_path = 'grocery_system.db'

def get_db_connection():
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = 1") # BẮT BUỘC: Bật chế độ kiểm tra khóa ngoại
    return conn

# --- PHẦN 1: HÀM UPDATE NGUYÊN LIỆU (INGREDIENTS) ---
def import_ingredient(cursor, data):
    """
    data: dict chứa thông tin nguyên liệu từ crawl
    Ví dụ: {'name': 'Trứng gà', 'unit': 'quả', 'category': 'Trứng', 'price': 3000}
    """
    try:
        # BƯỚC 1: Insert vào bảng GỐC recipe_components
        cursor.execute("INSERT INTO recipe_components (type) VALUES ('INGREDIENT')")
        comp_id = cursor.lastrowid # Lấy ID vừa sinh ra
        
        # BƯỚC 2: Insert vào bảng CON ingredients
        # Giả sử shelf_life mặc định là 7 ngày nếu không crawl được
        cursor.execute("""
            INSERT INTO ingredients (component_id, category, estimated_shelf_life, estimated_price)
            VALUES (?, ?, ?, ?)
        """, (comp_id, data.get('category'), data.get('shelf_life', 7), data.get('price', 0)))

        # BƯỚC 3: Insert vào bảng CHÁU (Phân loại đếm được/không đếm được)
        unit = data.get('unit', '').lower()
        name = data.get('name')
        
        # Logic phân loại đơn giản (Bạn có thể mở rộng list này)
        countable_units = ['quả', 'trái', 'hộp', 'gói', 'bó', 'lon']
        
        if unit in countable_units:
            cursor.execute("""
                INSERT INTO countable_ingredients (component_id, component_name, c_measurement_unit)
                VALUES (?, ?, ?)
            """, (comp_id, name, unit))
        else:
            # Mặc định các đơn vị khác (kg, g, l, ml...) vào uncountable
            cursor.execute("""
                INSERT INTO uncountable_ingredients (component_id, component_name, uc_measurement_unit)
                VALUES (?, ?, ?)
            """, (comp_id, name, unit))
            
        print(f"✅ Đã thêm nguyên liệu: {name} (ID: {comp_id})")
        return comp_id

    except sqlite3.IntegrityError as e:
        print(f"⚠️ Lỗi trùng lặp hoặc ràng buộc dữ liệu với {data.get('name')}: {e}")
        return None
    except Exception as e:
        print(f"❌ Lỗi không xác định: {e}")
        return None

# --- PHẦN 2: HÀM UPDATE MÓN ĂN (RECIPES) ---
def import_recipe(cursor, data, ingredient_map):
    """
    data: dict món ăn. Ví dụ: {'name': 'Trứng ốp la', 'steps': [...], 'ingredients': [{'name': 'Trứng gà', 'qty': 2}]}
    ingredient_map: dict để tra cứu tên nguyên liệu -> ID (ví dụ: {'trứng gà': 101})
    """
    try:
        # BƯỚC 1: Insert vào bảng GỐC
        cursor.execute("INSERT INTO recipe_components (type) VALUES ('RECIPE')")
        recipe_id = cursor.lastrowid
        
        # BƯỚC 2: Insert vào bảng RECIPES
        instructions_json = json.dumps(data.get('steps', [])) # Convert list bước làm thành JSON string
        cursor.execute("""
            INSERT INTO recipes (component_id, component_name, instructions, description, prep_time, cook_time)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (recipe_id, data['name'], instructions_json, data.get('description'), data.get('prep_time'), data.get('cook_time')))

        # BƯỚC 3: Insert vào bảng LIÊN KẾT (COMPONENT_LISTS)
        # Duyệt qua danh sách nguyên liệu của món ăn này
        for item in data.get('ingredients', []):
            ing_name_clean = item['name'].strip().lower()
            
            # Tra cứu ID nguyên liệu
            if ing_name_clean in ingredient_map:
                ing_id = ingredient_map[ing_name_clean]
                qty = item.get('qty', 0)
                
                cursor.execute("""
                    INSERT INTO component_lists (recipe_id, component_id, quantity)
                    VALUES (?, ?, ?)
                """, (recipe_id, ing_id, qty))
            else:
                print(f"   ⚠️ Cảnh báo: Món '{data['name']}' thiếu nguyên liệu '{item['name']}' trong DB")

        print(f"🍳 Đã thêm món: {data['name']} (ID: {recipe_id})")
        
    except sqlite3.IntegrityError as e:
        print(f"⚠️ Lỗi khi thêm món {data.get('name')}: {e}")

# --- PHẦN 3: MAIN EXECUTION ---
def main_pipeline():
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Load dữ liệu JSON (Giả sử bạn đã crawl xong)
    with open('ingredients.json', 'r', encoding='utf-8') as f:
        raw_ingredients = json.load(f)
    
    with open('recipes.json', 'r', encoding='utf-8') as f:
        raw_recipes = json.load(f)

    # 2. Chạy Import Nguyên liệu trước
    # Tạo map để tra cứu nhanh: {'tên nguyên liệu': id}
    name_to_id_map = {} 
    
    print("--- BẮT ĐẦU IMPORT NGUYÊN LIỆU ---")
    for ing in raw_ingredients:
        # Kiểm tra xem đã tồn tại chưa (đơn giản hóa bằng tên)
        # Trong thực tế bạn nên query DB để check
        new_id = import_ingredient(cursor, ing)
        if new_id:
            name_to_id_map[ing['name'].strip().lower()] = new_id
    
    conn.commit() # Lưu transaction đợt 1

    # 3. Chạy Import Món ăn sau
    print("\n--- BẮT ĐẦU IMPORT MÓN ĂN ---")
    for recipe in raw_recipes:
        import_recipe(cursor, recipe, name_to_id_map)
    
    conn.commit() # Lưu transaction đợt 2
    conn.close()
    print("\n🎉 HOÀN TẤT CẬP NHẬT DỮ LIỆU!")

if __name__ == "__main__":
    main_pipeline()