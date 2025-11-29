import sqlite3

def create_tables():
    conn = sqlite3.connect('./grocery_system.db')
    cursor = conn.cursor()

    # 1. Bảng cha: recipe_components (Nơi sinh ra ID duy nhất)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS recipe_components (
        component_id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL CHECK(type IN ('INGREDIENT', 'RECIPE'))
    );
    ''')

    # 2. Bảng ingredients (Thông tin chung của nguyên liệu)
    # Phục vụ chức năng quản lý thực phẩm [cite: 26] và hạn sử dụng [cite: 27]
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ingredients (
        component_id INTEGER PRIMARY KEY,
        category TEXT,
        estimated_shelf_life INTEGER,
        nutrition_per TEXT,
        protein REAL, fat REAL, carb REAL, fiber REAL, calories REAL,
        estimated_price INTEGER,
        ingredient_tag_list TEXT, -- Lưu JSON string
        FOREIGN KEY(component_id) REFERENCES recipe_components(component_id)
    );
    ''')

    # 3. Bảng con: countable_ingredients (Đếm được: quả, gói...)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS countable_ingredients (
        component_id INTEGER PRIMARY KEY,
        component_name TEXT NOT NULL,
        c_measurement_unit TEXT NOT NULL,
        FOREIGN KEY(component_id) REFERENCES ingredients(component_id),
        UNIQUE(component_name, c_measurement_unit)
    );
    ''')

    # 4. Bảng con: uncountable_ingredients (Không đếm được: g, ml...)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS uncountable_ingredients (
        component_id INTEGER PRIMARY KEY,
        component_name TEXT NOT NULL,
        uc_measurement_unit TEXT NOT NULL,
        FOREIGN KEY(component_id) REFERENCES ingredients(component_id),
        UNIQUE(component_name, uc_measurement_unit)
    );
    ''')

    # 5. Bảng recipes (Công thức nấu ăn)
    # Phục vụ chức năng hiển thị công thức [cite: 34]
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS recipes (
        component_id INTEGER PRIMARY KEY,
        component_name TEXT NOT NULL UNIQUE,
        category TEXT,
        image_url TEXT,
        prep_time TEXT, cook_time TEXT, default_servings INTEGER DEFAULT 1,
        level TEXT,
        instructions TEXT NOT NULL, -- Lưu JSON string
        FOREIGN KEY(component_id) REFERENCES recipe_components(component_id)
    );
    ''')

    # 6. Bảng liên kết: component_lists (Công thức gồm những nguyên liệu gì)
    # Phục vụ tính toán nguyên liệu cần mua [cite: 38]
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS component_lists (
        recipe_id INTEGER,
        component_id INTEGER,
        quantity REAL,
        PRIMARY KEY (recipe_id, component_id),
        FOREIGN KEY(recipe_id) REFERENCES recipes(component_id),
        FOREIGN KEY(component_id) REFERENCES recipe_components(component_id)
    );
    ''')

    conn.commit()
    conn.close()
    print("Đã khởi tạo database thành công!")

# Chạy hàm này 1 lần đầu tiên
create_tables()