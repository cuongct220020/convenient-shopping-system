# Test Cases cho Meal API

Base URL: `http://localhost:8003/v1/meals`

**Lưu ý:** Các test case này giả định rằng các recipe đã được tạo trước đó với các ID từ 12 đến 16.

---

## 1. COMMAND - Lần 1: Tạo bữa sáng và bữa trưa

### Test Case 1.1: Tạo bữa sáng và bữa trưa cho ngày 31/12/2025
**Method:** `POST`  
**URL:** `http://localhost:8003/v1/meals/command`  
**Body:**
```json
{
  "date": "2025-12-31",
  "group_id": 1,
  "breakfast": {
    "action": "upsert",
    "recipe_list": [
      {
        "recipe_id": 12,
        "recipe_name": "Salad cà chua",
        "servings": 2
      }
    ]
  },
  "lunch": {
    "action": "upsert",
    "recipe_list": [
      {
        "recipe_id": 13,
        "recipe_name": "Thịt lợn kho tàu",
        "servings": 4
      }
    ]
  },
  "dinner": {
    "action": "skip"
  }
}
```
**Expected Output:**
- Status Code: `200 OK`
- Response body là mảng chứa:
  - MealResponse cho breakfast (đã được tạo)
  - MealResponse cho lunch (đã được tạo)
  - MealMissingResponse cho dinner với `detail`: `"Meal has not been planned yet"` (dinner chưa được lên kế hoạch)
- Mỗi MealResponse chứa:
  - `meal_id`: số nguyên (ID được tạo tự động)
  - `date`: `"2025-12-31"`
  - `group_id`: 1
  - `meal_type`: `"breakfast"` hoặc `"lunch"`
  - `status`: `"created"`
  - `recipe_list`: mảng các recipe với `recipe_id`, `recipe_name`, `servings`
- MealMissingResponse cho dinner chứa:
  - `date`: `"2025-12-31"`
  - `group_id`: 1
  - `meal_type`: `"dinner"`
  - `detail`: `"Meal has not been planned yet"`

---

## 2. COMMAND - Lần 2: Xóa bữa sáng, tạo bữa tối, sửa bữa trưa

### Test Case 2.1: Xóa bữa sáng, tạo bữa tối, sửa bữa trưa cho ngày 31/12/2025
**Method:** `POST`  
**URL:** `http://localhost:8003/v1/meals/command`  
**Body:**
```json
{
  "date": "2025-12-31",
  "group_id": 1,
  "breakfast": {
    "action": "delete"
  },
  "lunch": {
    "action": "upsert",
    "recipe_list": [
      {
        "recipe_id": 14,
        "recipe_name": "Tôm rang me",
        "servings": 3
      },
      {
        "recipe_id": 15,
        "recipe_name": "Cơm chiên",
        "servings": 2
      }
    ]
  },
  "dinner": {
    "action": "upsert",
    "recipe_list": [
      {
        "recipe_id": 16,
        "recipe_name": "Bữa sáng đầy đủ",
        "servings": 2
      }
    ]
  }
}
```
**Expected Output:**
- Status Code: `200 OK`
- Response body là mảng chứa:
  - MealMissingResponse cho breakfast với `detail`: `"Meal deleted"` (đã xóa meal)
  - MealResponse cho lunch (đã được cập nhật với recipe_list mới)
  - MealResponse cho dinner (đã được tạo)
- MealMissingResponse cho breakfast chứa:
  - `date`: `"2025-12-31"`
  - `group_id`: 1
  - `meal_type`: `"breakfast"`
  - `detail`: `"Meal deleted"`
- MealResponse cho lunch:
  - `meal_id`: ID giữ nguyên (cùng meal_id từ lần 1)
  - `recipe_list`: mảng mới với 2 recipes (ID 14 và 15)
- MealResponse cho dinner:
  - `meal_id`: số nguyên mới (ID được tạo tự động)
  - `meal_type`: `"dinner"`
  - `recipe_list`: mảng với 1 recipe (ID 16)

---

## 3. GET - Lấy meals theo ngày

### Test Case 3.1: Lấy tất cả meals cho ngày 31/12/2025
**Method:** `GET`  
**URL:** `http://localhost:8003/v1/meals/?meal_date=2025-12-31&group_id=1`  
**Body:** Không có  
**Expected Output:**
- Status Code: `200 OK`
- Response body là mảng chứa 3 items:
  - MealMissingResponse cho breakfast với `detail`: `"Meal has not been planned yet"` (đã bị xóa ở Test Case 2.1)
  - MealResponse cho lunch (với recipe_list đã được cập nhật ở Test Case 2.1)
  - MealResponse cho dinner (đã được tạo ở Test Case 2.1)
- Thứ tự: breakfast, lunch, dinner
- MealResponse có đầy đủ thông tin: `meal_id`, `date`, `group_id`, `meal_type`, `status`, `recipe_list`
- MealMissingResponse có: `date`, `group_id`, `meal_type`, `detail`

---

### Test Case 3.2: Lấy bữa trưa cho ngày 31/12/2025
**Method:** `GET`  
**URL:** `http://localhost:8003/v1/meals/?meal_date=2025-12-31&group_id=1&meal_type=lunch`  
**Body:** Không có  
**Expected Output:**
- Status Code: `200 OK`
- Response body là mảng chứa 1 MealResponse:
  - Meal cho lunch với `meal_type`: `"lunch"`
  - `recipe_list` chứa 2 recipes (ID 14 và 15) như đã cập nhật ở Test Case 2.1

---

## Lưu ý

1. **Thứ tự thực hiện:** 
   - Chạy Test Case 1.1 trước (tạo breakfast và lunch)
   - Sau đó chạy Test Case 2.1 (xóa breakfast, sửa lunch, tạo dinner)
   - Cuối cùng chạy các Test Case 3.x để verify kết quả

2. **MealAction values:**
   - `"upsert"`: Tạo mới hoặc cập nhật meal (nếu đã tồn tại)
   - `"delete"`: Xóa meal
   - `"skip"`: Bỏ qua, không làm gì với meal đó

3. **MealType values:**
   - `"breakfast"` (bữa sáng)
   - `"lunch"` (bữa trưa)
   - `"dinner"` (bữa tối)

4. **MealStatus values:**
   - `"created"`: Meal đã được tạo
   - `"done"`: Meal đã hoàn thành
   - `"cancelled"`: Meal đã bị hủy
   - `"expired"`: Meal đã hết hạn

5. **Recipe List:**
   - Mỗi recipe trong `recipe_list` cần có `recipe_id`, `recipe_name`, và `servings`
   - `recipe_id` phải > 0
   - `servings` phải > 0
   - `recipe_name` là tên của recipe (có thể khác với tên trong recipe service, nhưng nên giữ đồng bộ)

6. **Date format:**
   - Sử dụng format ISO 8601: `YYYY-MM-DD`
   - Ví dụ: `"2025-12-31"`

7. **Unique constraint:**
   - Mỗi ngày và meal_type chỉ có thể có 1 meal duy nhất
   - Khi upsert với cùng date và meal_type, sẽ cập nhật meal hiện có thay vì tạo mới

8. **Verification:**
   - Sau mỗi command, nên thực hiện GET để xác nhận dữ liệu đã được tạo/cập nhật/xóa đúng
   - Meal ID sẽ giữ nguyên khi upsert (cập nhật), chỉ thay đổi khi tạo mới

