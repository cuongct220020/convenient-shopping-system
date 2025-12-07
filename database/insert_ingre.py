import sqlite3
import json

DB_PATH = 'grocery_system_v2.db'

def is_countable(unit_name):
    """
    Hàm xác định xem đơn vị này thuộc bảng Countable hay Uncountable.
    """
    unit_name = unit_name.lower()
    # Danh sách các đơn vị đo lường (không đếm được từng cái nguyên vẹn)
    uncountable_list = ['g', 'gr', 'gram', 'kg', 'ml', 'l', 'lít', 'muỗng', 'thìa', 'muỗng cà phê', 'thìa cà phê', 'chén', 'bát', 'ít', 'thìa canh', 'muỗng canh', 'muỗng cafe']
    
    if unit_name in uncountable_list:
        return False # Vào bảng Uncountable
    return True # Vào bảng Countable (quả, gói, hộp...)

def import_ingredients_text_per(json_data):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = 1")
    cursor = conn.cursor()

    print("🚀 Bắt đầu import dữ liệu...")

    for item in json_data:
        try:
            conn.execute("BEGIN TRANSACTION;")

            # 1. Insert bảng cha (recipe_components) để lấy ID
            cursor.execute("INSERT INTO recipe_components (type) VALUES ('INGREDIENT')")
            comp_id = cursor.lastrowid

            # 2. Xử lý dữ liệu dinh dưỡng
            # Lấy nguyên khối nutrition, nếu không có thì trả về dict rỗng
            nutri = item.get('nutrition', {})

            # Insert vào bảng ingredients
            # Lưu ý: Các chỉ số dinh dưỡng (fat, protein...) vẫn giữ là số để tính toán
            cursor.execute("""
                INSERT INTO ingredients 
                (component_id, category, protein, fat, carb, calories, 
                 estimated_shelf_life, estimated_price)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                comp_id, 
                item.get('category'), 
                nutri.get('protein', 0), 
                nutri.get('fat', 0), 
                nutri.get('carbs', 0), 
                nutri.get('calories', 0),
                365, # Shelf life mặc định
                0,   # Price mặc định
            ))

            # 3. Phân loại Countable / Uncountable (Logic cũ giữ nguyên)
            unit_val = item.get('unit', 'unknown')
            name_val = item.get('name')
            type_val = item.get('type')
            
            if type_val == 'countable':
                # Insert vào bảng đếm được
                cursor.execute("""
                    INSERT INTO countable_ingredients (component_id, component_name, c_measurement_unit)
                    VALUES (?, ?, ?)
                """, (comp_id, name_val, unit_val))
            else:
                # Insert vào bảng không đếm được (đo lường)
                cursor.execute("""
                    INSERT INTO uncountable_ingredients (component_id, component_name, uc_measurement_unit)
                    VALUES (?, ?, ?)
                """, (comp_id, name_val, unit_val))

            conn.commit()

        except sqlite3.IntegrityError as e:
            conn.rollback()
            print(f"⚠️ Trùng lặp hoặc lỗi ràng buộc: {item.get('name')} - {e}")
        except Exception as e:
            conn.rollback()
            print(f"❌ Lỗi xử lý {item.get('name')}: {e}")

    conn.close()

# --- CHẠY THỬ VỚI DỮ LIỆU CỦA BẠN ---
if __name__ == "__main__":
    with open('/home/gpus/hachi/convenient-shopping-system/crawler/data/ingredient_v7.json', 'r', encoding='utf-8') as f:
        raw_json = json.load(f)
    
    import_ingredients_text_per(raw_json)