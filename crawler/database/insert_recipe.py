import sqlite3
import json

DB_PATH = 'grocery_system_v2.db'

# --- HÀM LẤY MAP NGUYÊN LIỆU---
def get_ingredient_map_strict(cursor):
    print("⏳ Đang tải danh sách nguyên liệu (Name + Unit)...")
    
    # Lấy dữ liệu từ cả 2 bảng, đổi tên cột unit về chung 1 tên để dễ xử lý
    cursor.execute("""
        SELECT component_name, c_measurement_unit, component_id 
        FROM countable_ingredients
        UNION ALL
        SELECT component_name, uc_measurement_unit, component_id 
        FROM uncountable_ingredients
    """)
    
    rows = cursor.fetchall()
    
    # Tạo map: Key là tuple (tên, đơn vị), Value là ID
    # Lưu ý: convert hết về lowercase để so sánh chính xác hơn
    mapping = {}
    for row in rows:
        name = row[0].strip().lower()
        unit = row[1].strip().lower()
        comp_id = row[2]
        
        mapping[(name, unit)] = comp_id
        
    return mapping

# --- HÀM IMPORT RECIPES ---
def import_recipes_strict_check(json_data):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = 1")
    cursor = conn.cursor()

    # 1. Tải Map mới (Key là Tuple)
    ing_map_strict = get_ingredient_map_strict(cursor)
    
    # 2. Tạo thêm Map phụ chỉ có Name (để debug lỗi lệch đơn vị)
    # Nếu có nhiều unit cho 1 tên, nó sẽ lấy cái cuối cùng (chỉ dùng để check tồn tại)
    ing_map_fallback = {k[0]: v for k, v in ing_map_strict.items()}

    print("🚀 Bắt đầu import công thức (Chế độ kiểm tra Unit)...")

    for dish in json_data:
        try:
            conn.execute("BEGIN TRANSACTION;")

            # --- INSERT BẢNG CHA & RECIPES (Giữ nguyên như cũ) ---
            cursor.execute("INSERT INTO recipe_components (type) VALUES ('RECIPE')")
            recipe_id = cursor.lastrowid
            
            instr_json = json.dumps(dish.get('instructions', {}), ensure_ascii=False)
            cursor.execute("""
                INSERT INTO recipes 
                (component_id, component_name, category, image_url, prep_time, cook_time, default_servings, level, instructions)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                recipe_id, dish.get('name'), dish.get('category'), dish.get('img_url'),
                dish.get('pre_time', ''), dish.get('cook_time', ''), 
                dish.get('servings', 1), dish.get('level', ''), instr_json
            ))

            # --- INSERT COMPONENT LISTS (LOGIC MỚI) ---
            dish_ingredients = dish.get('ingredients', [])
            
            for ing in dish_ingredients:
                raw_name = ing.get('name', '').strip().lower()
                raw_unit = ing.get('unit', '').strip().lower()
                quantity = ing.get('quantity', 0)

                # Tạo key tìm kiếm: (tên, đơn vị)
                lookup_key = (raw_name, raw_unit)

                if lookup_key in ing_map_strict:
                    # TRƯỜNG HỢP 1: Khớp hoàn toàn cả Tên và Đơn vị
                    ing_db_id = ing_map_strict[lookup_key]
                    
                    cursor.execute("""
                        INSERT INTO component_lists (recipe_id, component_id, quantity)
                        VALUES (?, ?, ?)
                    """, (recipe_id, ing_db_id, quantity))
                    
                else:
                    # TRƯỜNG HỢP 2: Không khớp (có thể do lệch đơn vị hoặc chưa có tên)
                    if raw_name in ing_map_fallback:
                        # Đã có tên trong DB nhưng lệch đơn vị
                        # Ví dụ: JSON là 'thìa canh', DB là 'ml'
                        print(f"   ⚠️ Lệch đơn vị: Món '{dish['name']}' cần '{raw_name}' ({raw_unit}) -> DB có unit khác.")
                        
                        # TÙY CHỌN: Bạn có muốn insert đại cái ID tìm được theo tên không?
                        # Nếu muốn chấp nhận rủi ro để có data, hãy bỏ comment dòng dưới:
                        # db_id = ing_map_fallback[raw_name]
                        # cursor.execute("INSERT INTO component_lists...", (recipe_id, db_id, quantity))
                    else:
                        print(f"   ❌ Thiếu nguyên liệu: '{raw_name}' chưa có trong DB.")

            conn.commit()
            print(f"🍳 Đã thêm: {dish['name']}")

        except Exception as e:
            conn.rollback()
            print(f"❌ Lỗi xử lý món {dish.get('name')}: {e}")

    conn.close()

# --- CHẠY THỬ ---
if __name__ == "__main__":
    # Load file json recipes của bạn ở đây
    file = './crawler/data/recipe_v3.json'
    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    import_recipes_strict_check(data)