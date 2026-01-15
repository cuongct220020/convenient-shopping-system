# Đánh giá Index cho các Models

## Recipe Service

### 1. GroupPreference
- **user_id**: ✅ CẦN INDEX
  - Lý do: Được dùng trong WHERE clause (group_tags_handler.py:49, 75)
  - Query pattern: `WHERE user_id = ?` và `WHERE user_id = ? AND group_id IN (...)`

- **group_id**: ✅ CẦN INDEX  
  - Lý do: Được dùng trong WHERE clause (recommender.py:36, group_tags_handler.py:75)
  - Query pattern: `WHERE group_id = ?`

### 2. TagRelation
- Không cần index đơn lẻ - bảng nhỏ, chỉ có composite primary key

### 3. RecipeComponent
- **type**: ✅ ĐÃ CÓ INDEX (dòng 14 trong recipe_component.py)

### 4. Ingredient (base class)
- **category**: ✅ CẦN INDEX
  - Lý do: Được dùng trong WHERE clause với IN (ingredient_crud.py:94)
  - Query pattern: `WHERE category IN (...)`

### 5. CountableIngredient
- **component_name**: ✅ ĐÃ CÓ UNIQUE CONSTRAINT (tự động tạo index)

### 6. UncountableIngredient
- **component_name**: ⚠️ CÓ THỂ CẦN INDEX
  - Lý do: Được dùng trong ILIKE search (ingredient_crud.py:84)
  - Lưu ý: Index trên text với ILIKE pattern matching có thể không hiệu quả, nhưng vẫn nên có cho exact match

### 7. ComponentList
- **recipe_id**: ✅ CẦN INDEX (Foreign Key)
  - Lý do: Foreign key, được dùng trong JOINs và WHERE clauses
  - Query pattern: JOINs và `WHERE recipe_id = ?`

- **component_id**: ✅ CẦN INDEX (Foreign Key)
  - Lý do: Foreign key, được dùng trong JOINs và WHERE clauses
  - Query pattern: `WHERE component_id = ?` (ingredient_crud.py:68)

### 8. Recipe
- **component_name**: ✅ ĐÃ CÓ UNIQUE CONSTRAINT (tự động tạo index)
- **keywords**: ⚠️ JSONB - cần GIN index nhưng yêu cầu chỉ index đơn, nên bỏ qua

### 9. ComponentExistence
- **group_id**: ✅ ĐÃ CÓ PRIMARY KEY (tự động tạo index)

---

## Meal Service

### 1. Meal
- **date**: ✅ CẦN INDEX
  - Lý do: Được dùng thường xuyên trong WHERE clauses (meal_command_handler.py:33, 55, 68; expire_meals_task.py:14)
  - Query pattern: `WHERE date = ?`, `WHERE date < ?`

- **group_id**: ✅ CẦN INDEX
  - Lý do: Được dùng trong WHERE clauses (meal_command_handler.py:33, 55, 68)
  - Query pattern: `WHERE date = ? AND group_id = ? AND meal_type = ?`

- **meal_type**: ✅ CẦN INDEX
  - Lý do: Được dùng trong WHERE clauses (meal_command_handler.py:33, 55, 71)
  - Query pattern: `WHERE date = ? AND group_id = ? AND meal_type = ?`

- **meal_status**: ✅ CẦN INDEX
  - Lý do: Được dùng trong WHERE clauses (expire_meals_task.py:14, daily_meal_task.py:24)
  - Query pattern: `WHERE meal_status = ? AND date < ?`

### 2. RecipeList
- **meal_id**: ✅ CẦN INDEX (Foreign Key)
  - Lý do: Foreign key, được dùng trong relationships và JOINs

---

## Notification Service

### 1. Notification
- **group_id**: ✅ ĐÃ CÓ INDEX (dòng 15 trong notifications.py)

- **receiver**: ✅ ĐÃ CÓ INDEX (dòng 17 trong notifications.py)

- **is_read**: ✅ ĐÃ CÓ INDEX (dòng 21 trong notifications.py)

- **created_at**: ⚠️ CÓ THỂ CẦN INDEX
  - Lý do: Được dùng trong ORDER BY (notification_repository.py:24)
  - Query pattern: `ORDER BY created_at DESC`
  - Lưu ý: Nếu thường xuyên query với filter + sort, nên có index

---

## Shopping Storage Service

### 1. Storage
- **group_id**: ✅ CẦN INDEX
  - Lý do: Được dùng trong WHERE clauses và JOINs (report_process.py:77, storable_unit_crud.py:26, 72)
  - Query pattern: `WHERE group_id = ?`, JOIN với StorableUnit

- **storage_type**: ⚠️ CÓ THỂ CẦN INDEX
  - Lý do: Enum field, có thể được filter theo type
  - Tuy nhiên không thấy query pattern rõ ràng trong code

### 2. StorableUnit
- **storage_id**: ✅ CẦN INDEX (Foreign Key)
  - Lý do: Foreign key, được dùng trong WHERE clauses (storable_unit_crud.py:119, 151)
  - Query pattern: `WHERE storage_id = ?`, JOINs

- **expiration_date**: ✅ CẦN INDEX
  - Lý do: Được dùng trong WHERE clause cho expiration tasks (expire_units_task.py:35)
  - Query pattern: `WHERE expiration_date IN (?, ?)` - rất quan trọng cho scheduled tasks

- **component_id**: ✅ CẦN INDEX
  - Lý do: Được dùng trong WHERE clauses với IS NOT NULL (storable_unit_crud.py:27, 73, 78)
  - Query pattern: `WHERE component_id IS NOT NULL`

- **unit_name**: ⚠️ CÓ THỂ CẦN INDEX
  - Lý do: Được dùng trong WHERE clauses (storable_unit_crud.py:155, 157)
  - Query pattern: `WHERE unit_name IN (...)`, `WHERE unit_name = ?`
  - Lưu ý: Nếu thường xuyên query theo tên, nên có index

### 3. ShoppingPlan
- **group_id**: ✅ CẦN INDEX
  - Lý do: Được dùng trong WHERE clause (plan_crud.py:30)
  - Query pattern: `WHERE group_id = ?`

- **plan_status**: ✅ CẦN INDEX
  - Lý do: Được dùng trong WHERE clauses (plan_crud.py:33, expire_plans_task.py:21)
  - Query pattern: `WHERE plan_status IN (?, ?)`

- **deadline**: ✅ CẦN INDEX
  - Lý do: Được dùng trong WHERE clauses (plan_crud.py:42, expire_plans_task.py:22)
  - Query pattern: `WHERE deadline >= ? AND deadline < ?`, `WHERE deadline < ?`
  - Rất quan trọng cho scheduled expiration tasks

- **assigner_id**: ⚠️ CÓ THỂ CẦN INDEX
  - Lý do: Có thể được query để tìm plans của một user
  - Tuy nhiên không thấy query pattern rõ ràng trong code

- **assignee_id**: ⚠️ CÓ THỂ CẦN INDEX
  - Lý do: Có thể được query để tìm plans được assign cho một user
  - Tuy nhiên không thấy query pattern rõ ràng trong code

### 4. Report
- **plan_id**: ✅ ĐÃ CÓ UNIQUE CONSTRAINT (tự động tạo index)

---

## Tóm tắt các Index cần thêm

### Recipe Service:
1. `group_preferences.user_id`
2. `group_preferences.group_id`
3. `ingredients.category`
4. `component_lists.recipe_id`
5. `component_lists.component_id`

### Meal Service:
1. `meals.date`
2. `meals.group_id`
3. `meals.meal_type`
4. `meals.meal_status`
5. `recipe_lists.meal_id`

### Notification Service:
- Tất cả các index quan trọng đã có sẵn

### Shopping Storage Service:
1. `storages.group_id`
2. `storable_units.storage_id`
3. `storable_units.expiration_date`
4. `storable_units.component_id`
5. `shopping_plans.group_id`
6. `shopping_plans.plan_status`
7. `shopping_plans.deadline`

