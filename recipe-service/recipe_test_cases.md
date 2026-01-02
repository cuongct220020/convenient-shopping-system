# Test Cases cho Recipe API

Base URL: `http://localhost:8001/v2/recipes`

**Lưu ý:** Các test case này giả định rằng các ingredient đã được tạo trước đó với các ID sau:
- ID 1: Cà chua
- ID 2: Thịt lợn
- ID 4: Tôm
- ID 5: Chuối
- ID 6: Tỏi
- ID 7: Sữa tươi
- ID 8: Gạo trắng
- ID 9: Dầu ăn
- ID 10: Bánh mì
- ID 11: Trứng gà

---

## 1. CREATE - Tạo 5 recipes

### Test Case 1.1: Tạo recipe đơn giản - Salad cà chua
**Method:** `POST`  
**URL:** `http://localhost:8001/v2/recipes/`  
**Body:**
```json
{
  "component_name": "Salad cà chua",
  "level": "Dễ",
  "default_servings": 2,
  "prep_time": 10,
  "cook_time": 10,
  "instructions": [
    "Rửa sạch cà chua và cắt thành lát mỏng",
    "Băm nhỏ tỏi",
    "Trộn cà chua với dầu ăn và tỏi",
    "Thêm gia vị và thưởng thức"
  ],
  "keywords": ["salad", "cà chua", "rau củ", "ăn kiêng"],
  "component_list": [
    {
      "component_id": 1,
      "quantity": 4
    },
    {
      "component_id": 6,
      "quantity": 2
    },
    {
      "component_id": 9,
      "quantity": 15
    }
  ]
}
```
**Expected Output:**
- Status Code: `201 Created`
- Response body chứa:
  - `component_id`: số nguyên (ID được tạo tự động)
  - `component_name`: `"Salad cà chua"`
  - `level`: `"Dễ"`
  - `default_servings`: 2
  - `prep_time`: 10
  - `cook_time`: 0
  - `instructions`: mảng các bước hướng dẫn
  - `keywords`: mảng keywords
  - `component_list`: mảng các component với `component_id` và `quantity`

---

### Test Case 1.2: Tạo recipe trung bình - Thịt lợn kho tàu
**Method:** `POST`  
**URL:** `http://localhost:8001/v2/recipes/`  
**Body:**
```json
{
  "component_name": "Thịt lợn kho tàu",
  "level": "Trung bình",
  "default_servings": 4,
  "prep_time": 15,
  "cook_time": 45,
  "instructions": [
    "Rửa sạch thịt lợn và cắt thành miếng vừa ăn",
    "Ướp thịt với tỏi băm và gia vị trong 15 phút",
    "Đun nóng dầu ăn, cho thịt vào xào sơ",
    "Thêm nước và kho nhỏ lửa trong 45 phút",
    "Nêm nếm lại và tắt bếp"
  ],
  "keywords": ["thịt lợn", "kho tàu", "món mặn", "cơm"],
  "component_list": [
    {
      "component_id": 2,
      "quantity": 4
    },
    {
      "component_id": 6,
      "quantity": 3
    },
    {
      "component_id": 9,
      "quantity": 20
    }
  ]
}
```
**Expected Output:**
- Status Code: `201 Created`
- Response chứa `component_id` mới và thông tin đã tạo

---

### Test Case 1.3: Tạo recipe trung bình - Tôm rang me
**Method:** `POST`  
**URL:** `http://localhost:8001/v2/recipes/`  
**Body:**
```json
{
  "component_name": "Tôm rang me",
  "level": "Trung bình",
  "default_servings": 3,
  "prep_time": 20,
  "cook_time": 15,
  "instructions": [
    "Rửa sạch tôm, cắt bỏ râu và chân",
    "Băm nhỏ tỏi",
    "Đun nóng dầu ăn, phi thơm tỏi",
    "Cho tôm vào rang đến khi chín vàng",
    "Thêm nước me và nêm nếm",
    "Rang thêm 5 phút cho tôm thấm vị"
  ],
  "keywords": ["tôm", "rang me", "hải sản", "chua ngọt"],
  "component_list": [
    {
      "component_id": 4,
      "quantity": 10
    },
    {
      "component_id": 6,
      "quantity": 2
    },
    {
      "component_id": 9,
      "quantity": 25
    }
  ]
}
```
**Expected Output:**
- Status Code: `201 Created`
- Response chứa thông tin tôm rang me đã tạo

---

### Test Case 1.4: Tạo recipe nested - Cơm chiên (chứa recipe khác)
**Method:** `POST`  
**URL:** `http://localhost:8001/v2/recipes/`  
**Body:**
```json
{
  "component_name": "Cơm chiên",
  "level": "Khó",
  "default_servings": 4,
  "prep_time": 30,
  "cook_time": 20,
  "instructions": [
    "Nấu cơm và để nguội",
    "Chuẩn bị thịt lợn kho tàu theo công thức",
    "Đánh trứng và chiên thành trứng chưng",
    "Đun nóng dầu ăn, cho cơm vào chiên",
    "Thêm thịt lợn kho tàu và trứng vào",
    "Đảo đều và nêm nếm",
    "Chiên đến khi cơm vàng và thơm"
  ],
  "keywords": ["cơm chiên", "thịt lợn", "trứng", "món chính"],
  "component_list": [
    {
      "component_id": 8,
      "quantity": 400
    },
    {
      "component_id": 2,
      "quantity": 1
    },
    {
      "component_id": 11,
      "quantity": 2
    },
    {
      "component_id": 9,
      "quantity": 30
    }
  ]
}
```
**Expected Output:**
- Status Code: `201 Created`
- Response body chứa:
  - `component_id`: số nguyên (ID được tạo tự động)
  - `component_list` chứa cả ingredient (gạo trắng ID 8, trứng gà ID 11, dầu ăn ID 9) và recipe (thịt lợn kho tàu với component_id = 2)
  - Tất cả các trường khác đầy đủ

**Lưu ý:** `component_id: 2` trong `component_list` là ID của recipe "Thịt lợn kho tàu" đã tạo ở Test Case 1.2 (nested recipe). Cần đảm bảo đã tạo recipe "Thịt lợn kho tàu" trước và sử dụng đúng component_id của nó.

---

### Test Case 1.5: Tạo recipe nested - Bữa sáng đầy đủ (chứa recipe khác)
**Method:** `POST`  
**URL:** `http://localhost:8001/v2/recipes/`  
**Body:**
```json
{
  "component_name": "Bữa sáng đầy đủ",
  "level": "Khó",
  "default_servings": 2,
  "prep_time": 25,
  "cook_time": 15,
  "instructions": [
    "Chuẩn bị salad cà chua theo công thức",
    "Chiên trứng ốp la",
    "Làm nóng bánh mì",
    "Pha sữa tươi",
    "Bày tất cả lên đĩa và thưởng thức"
  ],
  "keywords": ["bữa sáng", "đầy đủ", "salad", "trứng", "bánh mì"],
  "component_list": [
    {
      "component_id": 1,
      "quantity": 1
    },
    {
      "component_id": 10,
      "quantity": 2
    },
    {
      "component_id": 11,
      "quantity": 2
    },
    {
      "component_id": 7,
      "quantity": 250
    }
  ]
}
```
**Expected Output:**
- Status Code: `201 Created`
- Response body chứa:
  - `component_id`: số nguyên (ID được tạo tự động)
  - `component_list` chứa cả ingredient (bánh mì ID 10, trứng gà ID 11, sữa tươi ID 7) và recipe (salad cà chua với component_id = 1)
  - Tất cả các trường khác đầy đủ

**Lưu ý:** `component_id: 1` trong `component_list` là ID của recipe "Salad cà chua" đã tạo ở Test Case 1.1 (nested recipe). Cần đảm bảo đã tạo recipe "Salad cà chua" trước và sử dụng đúng component_id của nó.

---

## 2. GET - Lấy recipe theo ID

### Test Case 2.1: Lấy recipe theo ID (ID từ Test Case 1.1)
**Method:** `GET`  
**URL:** `http://localhost:8001/v2/recipes/{id}`  
(Thay `{id}` bằng component_id thực tế từ Test Case 1.1)  
**Body:** Không có  
**Expected Output:**
- Status Code: `200 OK`
- Response body chứa thông tin recipe với `component_id` đã yêu cầu
- Bao gồm đầy đủ các trường: `component_id`, `component_name`, `level`, `default_servings`, `instructions`, `keywords`, `component_list`
- Thông tin khớp với dữ liệu đã tạo ở Test Case 1.1

---

### Test Case 2.2: Lấy recipe theo ID (ID từ Test Case 1.3)
**Method:** `GET`  
**URL:** `http://localhost:8001/v2/recipes/{id}`  
(Thay `{id}` bằng component_id thực tế từ Test Case 1.3)  
**Body:** Không có  
**Expected Output:**
- Status Code: `200 OK`
- Response body chứa thông tin recipe đầy đủ, khớp với dữ liệu đã tạo ở Test Case 1.3

---

## 3. GET MANY - Lấy danh sách recipes (Pagination)

### Test Case 3.1: Lấy trang đầu tiên (5 items)
**Method:** `GET`  
**URL:** `http://localhost:8001/v2/recipes/?limit=5`  
**Body:** Không có  
**Expected Output:**
- Status Code: `200 OK`
- Response body có dạng:
```json
{
  "data": [
    // 5 recipes đầu tiên
  ],
  "next_cursor": 5,
  "size": 5
}
```
- `data`: mảng chứa 5 recipes
- `next_cursor`: ID của recipe cuối cùng (để dùng cho lần pagination tiếp theo)
- `size`: 5

---

### Test Case 3.2: Lấy trang thứ hai (5 items tiếp theo)
**Method:** `GET`  
**URL:** `http://localhost:8001/v2/recipes/?cursor={next_cursor}&limit=5`  
(Thay `{next_cursor}` bằng giá trị từ Test Case 3.1)  
**Body:** Không có  
**Expected Output:**
- Status Code: `200 OK`
- Response body có dạng:
```json
{
  "data": [
    // 5 recipes tiếp theo (từ ID > cursor)
  ],
  "next_cursor": số hoặc null,
  "size": 5 hoặc ít hơn
}
```
- `data`: mảng chứa 5 recipes tiếp theo (hoặc ít hơn nếu hết dữ liệu)
- Các items có ID lớn hơn `cursor` từ request

---

## 4. SEARCH - Tìm kiếm recipes

### Test Case 4.1: Tìm kiếm với keyword "thịt"
**Method:** `GET`  
**URL:** `http://localhost:8001/v2/recipes/search?keyword=thịt&limit=5`  
**Body:** Không có  
**Expected Output:**
- Status Code: `200 OK`
- Response body có dạng:
```json
{
  "data": [
    // Các recipes có tên hoặc keywords chứa "thịt"
  ],
  "next_cursor": số hoặc null,
  "size": số lượng kết quả
}
```
- `data`: mảng chứa các recipes có `component_name` hoặc `keywords` chứa keyword "thịt"
- Ít nhất chứa recipe "Thịt lợn kho tàu" đã tạo ở Test Case 1.2

---

### Test Case 4.2: Tìm kiếm với keyword "salad"
**Method:** `GET`  
**URL:** `http://localhost:8001/v2/recipes/search?keyword=salad&limit=5`  
**Body:** Không có  
**Expected Output:**
- Status Code: `200 OK`
- Response body có dạng:
```json
{
  "data": [
    // Các recipes có tên hoặc keywords chứa "salad"
  ],
  "next_cursor": số hoặc null,
  "size": số lượng kết quả
}
```
- `data`: mảng chứa các recipes có `component_name` hoặc `keywords` chứa keyword "salad"
- Ít nhất chứa recipe "Salad cà chua" đã tạo ở Test Case 1.1

---

## 5. DETAILED - Lấy recipe chi tiết với nested structure

### Test Case 5.1: Lấy recipe chi tiết (nested recipe - Cơm chiên)
**Method:** `GET`  
**URL:** `http://localhost:8001/v2/recipes/detailed/{id}`  
(Thay `{id}` bằng component_id thực tế từ Test Case 1.4 - Cơm chiên)  
**Body:** Không có  
**Expected Output:**
- Status Code: `200 OK`
- Response body có dạng:
```json
{
  "component_id": số,
  "component_name": "Cơm chiên",
  "type": "recipe",
  "level": "Khó",
  "default_servings": 4,
  "instructions": [...],
  "keywords": [...],
  "component_list": [
    {
      "quantity": số,
      "component": {
        // Ingredient response hoặc RecipeDetailedResponse (nested)
      }
    }
  ]
}
```
- `component_list`: mảng các component với thông tin chi tiết
- Component có `component_id` là ingredient sẽ hiển thị thông tin ingredient đầy đủ
- Component có `component_id` là recipe (thịt lợn kho tàu) sẽ hiển thị nested structure với `type: "recipe"` và `component_list` của nó
- Tất cả nested recipes được expand đầy đủ

---

## 6. FLATTENED - Aggregate ingredients từ nhiều recipes

### Test Case 6.1: Aggregate ingredients từ 2 recipes (không check existence)
**Method:** `POST`  
**URL:** `http://localhost:8001/v2/recipes/flattened?check_existence=false`  
**Body:**
```json
[
  {
    "recipe_id": 1,
    "quantity": 2
  },
  {
    "recipe_id": 2,
    "quantity": 1
  }
]
```
(Thay `recipe_id: 1` và `recipe_id: 2` bằng component_id thực tế từ Test Case 1.1 và 1.2)  
**Expected Output:**
- Status Code: `200 OK`
- Response body có dạng:
```json
{
  "ingredients": [
    {
      "quantity": số (tổng hợp từ các recipes),
      "ingredient": {
        // IngredientResponse đầy đủ
      },
      "available": null
    }
  ]
}
```
- `ingredients`: mảng các ingredient đã được aggregate và tổng hợp quantity
- Các ingredient trùng lặp được gộp lại và cộng quantity
- `available`: null (vì không check existence)

---

### Test Case 6.2: Aggregate ingredients với check existence (cần group_id)
**Method:** `POST`  
**URL:** `http://localhost:8001/v2/recipes/flattened?check_existence=true&group_id=1`  
**Body:**
```json
[
  {
    "recipe_id": 1,
    "quantity": 1
  },
  {
    "recipe_id": 3,
    "quantity": 1
  }
]
```
(Thay `recipe_id: 1` và `recipe_id: 3` bằng component_id thực tế từ Test Case 1.1 và 1.3)  
**Expected Output:**
- Status Code: `200 OK`
- Response body có dạng:
```json
{
  "ingredients": [
    {
      "quantity": số,
      "ingredient": {
        // IngredientResponse đầy đủ
      },
      "available": true hoặc false
    }
  ]
}
```
- `ingredients`: mảng các ingredient đã được aggregate
- `available`: boolean cho biết ingredient có sẵn trong group inventory hay không
- Nếu group_id không tồn tại hoặc ingredient không có trong inventory, `available` sẽ là false

---

## 7. UPDATE - Cập nhật recipe

### Test Case 7.1: Cập nhật recipe (Salad cà chua)
**Method:** `PUT`  
**URL:** `http://localhost:8001/v2/recipes/{id}`  
(Thay `{id}` bằng component_id thực tế từ Test Case 1.1)  
**Body:**
```json
{
  "component_name": "Salad cà chua cải tiến",
  "default_servings": 3,
  "prep_time": 15,
  "instructions": [
    "Rửa sạch cà chua và cắt thành lát mỏng",
    "Băm nhỏ tỏi",
    "Trộn cà chua với dầu ăn và tỏi",
    "Thêm gia vị và thưởng thức",
    "Trang trí với rau thơm"
  ],
  "keywords": ["salad", "cà chua", "rau củ", "ăn kiêng", "healthy"]
}
```
**Expected Output:**
- Status Code: `200 OK`
- Response body chứa:
  - `component_id`: ID không đổi
  - `component_name`: `"Salad cà chua cải tiến"` (đã được cập nhật)
  - `default_servings`: 3 (đã được cập nhật)
  - `prep_time`: 15 (đã được cập nhật)
  - `instructions`: mảng mới với 5 bước (đã được cập nhật)
  - `keywords`: mảng mới với keyword "healthy" (đã được cập nhật)
  - Các trường khác giữ nguyên giá trị cũ

---

### Test Case 7.2: Cập nhật một phần thông tin recipe (Thịt lợn kho tàu)
**Method:** `PUT`  
**URL:** `http://localhost:8001/v2/recipes/{id}`  
(Thay `{id}` bằng component_id thực tế từ Test Case 1.2)  
**Body:**
```json
{
  "cook_time": 60,
  "level": "Khó"
}
```
**Expected Output:**
- Status Code: `200 OK`
- Response body chứa:
  - `component_id`: ID không đổi
  - `cook_time`: 60 (đã được cập nhật)
  - `level`: `"Khó"` (đã được cập nhật)
  - `component_name`: `"Thịt lợn kho tàu"` (giữ nguyên)
  - Các trường khác giữ nguyên giá trị cũ

---

### Test Case 7.3: Cập nhật component_list của recipe
**Method:** `PUT`  
**URL:** `http://localhost:8001/v2/recipes/{id}`  
(Thay `{id}` bằng component_id thực tế từ Test Case 1.3)  
**Body:**
```json
{
  "component_list": [
    {
      "component_id": 4,
      "quantity": 15
    },
    {
      "component_id": 6,
      "quantity": 3
    },
    {
      "component_id": 9,
      "quantity": 30
    }
  ]
}
```
**Expected Output:**
- Status Code: `200 OK`
- Response body chứa:
  - `component_id`: ID không đổi
  - `component_list`: mảng mới với quantity đã được cập nhật
  - Tất cả các trường khác giữ nguyên

---

### Test Case 7.4: Sửa nested recipe trong Cơm chiên (component_id = 13)
**Method:** `PUT`  
**URL:** `http://localhost:8001/v2/recipes/{id}`  
(Thay `{id}` bằng component_id thực tế từ Test Case 1.4 - Cơm chiên)  
**Body:**
```json
{
  "component_list": [
    {
      "component_id": 8,
      "quantity": 400
    },
    {
      "component_id": 13,
      "quantity": 1
    },
    {
      "component_id": 11,
      "quantity": 2
    },
    {
      "component_id": 9,
      "quantity": 30
    }
  ]
}
```
**Expected Output:**
- Status Code: `200 OK`
- Response body chứa:
  - `component_id`: ID không đổi
  - `component_list`: mảng mới với `component_id: 13` thay vì `component_id: 2` (recipe "Thịt lợn kho tàu" với ID đúng là 13)
  - Tất cả các trường khác giữ nguyên

**Lưu ý:** Test case này sửa lại nested recipe trong "Cơm chiên" để sử dụng đúng component_id = 13 của recipe "Thịt lợn kho tàu".

---

### Test Case 7.5: Sửa nested recipe trong Bữa sáng đầy đủ (component_id = 12)
**Method:** `PUT`  
**URL:** `http://localhost:8001/v2/recipes/{id}`  
(Thay `{id}` bằng component_id thực tế từ Test Case 1.5 - Bữa sáng đầy đủ)  
**Body:**
```json
{
  "component_list": [
    {
      "component_id": 12,
      "quantity": 1
    },
    {
      "component_id": 10,
      "quantity": 2
    },
    {
      "component_id": 11,
      "quantity": 2
    },
    {
      "component_id": 7,
      "quantity": 250
    }
  ]
}
```
**Expected Output:**
- Status Code: `200 OK`
- Response body chứa:
  - `component_id`: ID không đổi
  - `component_list`: mảng mới với `component_id: 12` thay vì `component_id: 1` (recipe "Salad cà chua" với ID đúng là 12)
  - Tất cả các trường khác giữ nguyên

**Lưu ý:** Test case này sửa lại nested recipe trong "Bữa sáng đầy đủ" để sử dụng đúng component_id = 12 của recipe "Salad cà chua".

---

## Lưu ý

1. **Thứ tự thực hiện:** 
   - Đảm bảo đã tạo tất cả ingredients trước khi tạo recipes
   - Tạo recipes theo thứ tự: Test Case 1.1, 1.2, 1.3 trước
   - Sau đó mới tạo Test Case 1.4 và 1.5 (vì chúng chứa nested recipes)
   - **Quan trọng:** Sau khi tạo xong tất cả recipes, cần chạy Test Case 7.4 và 7.5 để sửa lại nested recipe IDs cho đúng:
     - Test Case 7.4: Sửa "Cơm chiên" để nested recipe "Thịt lợn kho tàu" có component_id = 13
     - Test Case 7.5: Sửa "Bữa sáng đầy đủ" để nested recipe "Salad cà chua" có component_id = 12

2. **Nested Recipes:**
   - Test Case 1.4 tạo "Cơm chiên" với nested recipe "Thịt lợn kho tàu" (component_id = 2 ban đầu, sẽ được sửa thành 13 ở Test Case 7.4)
   - Test Case 1.5 tạo "Bữa sáng đầy đủ" với nested recipe "Salad cà chua" (component_id = 1 ban đầu, sẽ được sửa thành 12 ở Test Case 7.5)
   - Sau khi chạy Test Case 7.4 và 7.5, các nested recipes sẽ có component_id đúng

3. **Level values:**
   - `"Dễ"` (EASY)
   - `"Trung bình"` (MEDIUM)
   - `"Khó"` (HARD)

4. **Component List:**
   - Mỗi component trong `component_list` cần có `component_id` (ID của ingredient hoặc recipe) và `quantity` (số lượng)
   - `quantity` phải > 0
   - Có thể mix ingredient và recipe trong cùng một `component_list`

5. **Pagination:**
   - Sử dụng cursor-based pagination
   - `next_cursor` là ID của item cuối cùng trong trang hiện tại
   - Nếu `next_cursor` là null, nghĩa là đã hết dữ liệu

6. **Flattened endpoint:**
   - `check_existence=false`: không cần `group_id`, `available` sẽ là null
   - `check_existence=true`: bắt buộc phải có `group_id`, `available` sẽ là boolean
   - Nếu thiếu `group_id` khi `check_existence=true`, sẽ trả về 400 Bad Request

7. **Update endpoint:**
   - Chỉ cần gửi các trường muốn cập nhật, không cần gửi tất cả
   - Không thể cập nhật `component_list` để chứa chính recipe đó (sẽ trả về 400)

8. **Verification:**
   - Sau khi tạo recipe, nên thực hiện GET để xác nhận dữ liệu đã được tạo đúng
   - Với nested recipes, sử dụng endpoint `/v2/recipes/detailed/{id}` để xem chi tiết component_list với nested structure
