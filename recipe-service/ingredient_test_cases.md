# Test Cases cho Ingredient API

Base URL: `http://localhost:8001/v2/ingredients`

---

## 1. CREATE - Tạo 10 nguyên liệu đủ thể loại

### Test Case 1.1: Tạo nguyên liệu đếm được - Rau củ (Cà chua)
**Method:** `POST`  
**URL:** `http://localhost:8001/v2/ingredients/`  
**Body:**
```json
{
  "type": "countable_ingredient",
  "component_name": "Cà chua",
  "category": "Rau củ",
  "c_measurement_unit": "quả",
  "estimated_shelf_life": 7,
  "protein": 0.9,
  "fat": 0.2,
  "carb": 3.9,
  "fiber": 1.2,
  "calories": 18,
  "estimated_price": 5000
}
```
**Expected Output:**
- Status Code: `201 Created`
- Response body chứa:
  - `component_id`: số nguyên (ID được tạo tự động)
  - `type`: `"countable_ingredient"`
  - `component_name`: `"Cà chua"`
  - `category`: `"Rau củ"`
  - `c_measurement_unit`: `"quả"`
  - Các trường khác giống như input

---

### Test Case 1.2: Tạo nguyên liệu đếm được - Thịt tươi (Thịt lợn)
**Method:** `POST`  
**URL:** `http://localhost:8001/v2/ingredients/`  
**Body:**
```json
{
  "type": "countable_ingredient",
  "component_name": "Thịt lợn",
  "category": "Thịt tươi",
  "c_measurement_unit": "miếng",
  "estimated_shelf_life": 3,
  "protein": 27.0,
  "fat": 14.0,
  "carb": 0.0,
  "fiber": 0.0,
  "calories": 242,
  "estimated_price": 150000
}
```
**Expected Output:**
- Status Code: `201 Created`
- Response chứa `component_id` mới và thông tin đã tạo

---

### Test Case 1.3: Tạo nguyên liệu đếm được - Hải sản (Tôm)
**Method:** `POST`  
**URL:** `http://localhost:8001/v2/ingredients/`  
**Body:**
```json
{
  "type": "countable_ingredient",
  "component_name": "Tôm",
  "category": "Hải sản và cá viên",
  "c_measurement_unit": "con",
  "estimated_shelf_life": 2,
  "protein": 24.0,
  "fat": 0.3,
  "carb": 0.2,
  "fiber": 0.0,
  "calories": 99,
  "estimated_price": 200000
}
```
**Expected Output:**
- Status Code: `201 Created`
- Response chứa thông tin tôm đã tạo

---

### Test Case 1.4: Tạo nguyên liệu đếm được - Trái cây tươi (Chuối)
**Method:** `POST`  
**URL:** `http://localhost:8001/v2/ingredients/`  
**Body:**
```json
{
  "type": "countable_ingredient",
  "component_name": "Chuối",
  "category": "Trái cây tươi",
  "c_measurement_unit": "quả",
  "estimated_shelf_life": 5,
  "protein": 1.1,
  "fat": 0.3,
  "carb": 23.0,
  "fiber": 2.6,
  "calories": 89,
  "estimated_price": 15000
}
```
**Expected Output:**
- Status Code: `201 Created`
- Response chứa thông tin chuối đã tạo

---

### Test Case 1.5: Tạo nguyên liệu đếm được - Gia vị (Tỏi)
**Method:** `POST`  
**URL:** `http://localhost:8001/v2/ingredients/`  
**Body:**
```json
{
  "type": "countable_ingredient",
  "component_name": "Tỏi",
  "category": "Gia vị",
  "c_measurement_unit": "củ",
  "estimated_shelf_life": 30,
  "protein": 6.4,
  "fat": 0.5,
  "carb": 33.0,
  "fiber": 2.1,
  "calories": 149,
  "estimated_price": 20000
}
```
**Expected Output:**
- Status Code: `201 Created`
- Response chứa thông tin tỏi đã tạo

---

### Test Case 1.6: Tạo nguyên liệu không đếm được - Sữa
**Method:** `POST`  
**URL:** `http://localhost:8001/v2/ingredients/`  
**Body:**
```json
{
  "type": "uncountable_ingredient",
  "component_name": "Sữa tươi",
  "category": "Sữa",
  "uc_measurement_unit": "ML",
  "estimated_shelf_life": 7,
  "protein": 3.3,
  "fat": 3.6,
  "carb": 4.8,
  "fiber": 0.0,
  "calories": 61,
  "estimated_price": 25000
}
```
**Expected Output:**
- Status Code: `201 Created`
- Response chứa:
  - `type`: `"uncountable_ingredient"`
  - `uc_measurement_unit`: `"ML"`
  - `component_id` và các thông tin khác

---

### Test Case 1.7: Tạo nguyên liệu không đếm được - Gạo
**Method:** `POST`  
**URL:** `http://localhost:8001/v2/ingredients/`  
**Body:**
```json
{
  "type": "uncountable_ingredient",
  "component_name": "Gạo trắng",
  "category": "Lương thực",
  "uc_measurement_unit": "G",
  "estimated_shelf_life": 365,
  "protein": 7.1,
  "fat": 0.7,
  "carb": 77.0,
  "fiber": 0.4,
  "calories": 365,
  "estimated_price": 30000
}
```
**Expected Output:**
- Status Code: `201 Created`
- Response chứa thông tin gạo đã tạo với `uc_measurement_unit`: `"G"`

---

### Test Case 1.8: Tạo nguyên liệu không đếm được - Dầu ăn
**Method:** `POST`  
**URL:** `http://localhost:8001/v2/ingredients/`  
**Body:**
```json
{
  "type": "uncountable_ingredient",
  "component_name": "Dầu ăn",
  "category": "Gia vị",
  "uc_measurement_unit": "ML",
  "estimated_shelf_life": 180,
  "protein": 0.0,
  "fat": 100.0,
  "carb": 0.0,
  "fiber": 0.0,
  "calories": 884,
  "estimated_price": 50000
}
```
**Expected Output:**
- Status Code: `201 Created`
- Response chứa thông tin dầu ăn đã tạo

---

### Test Case 1.9: Tạo nguyên liệu đếm được - Bánh mì
**Method:** `POST`  
**URL:** `http://localhost:8001/v2/ingredients/`  
**Body:**
```json
{
  "type": "countable_ingredient",
  "component_name": "Bánh mì",
  "category": "Bánh ngọt",
  "c_measurement_unit": "củ",
  "estimated_shelf_life": 2,
  "protein": 9.0,
  "fat": 3.2,
  "carb": 49.0,
  "fiber": 2.7,
  "calories": 265,
  "estimated_price": 10000
}
```
**Expected Output:**
- Status Code: `201 Created`
- Response chứa thông tin bánh mì đã tạo

---

### Test Case 1.10: Tạo nguyên liệu đếm được - Trứng
**Method:** `POST`  
**URL:** `http://localhost:8001/v2/ingredients/`  
**Body:**
```json
{
  "type": "countable_ingredient",
  "component_name": "Trứng gà",
  "category": "Khác",
  "c_measurement_unit": "quả",
  "estimated_shelf_life": 30,
  "protein": 13.0,
  "fat": 11.0,
  "carb": 1.1,
  "fiber": 0.0,
  "calories": 155,
  "estimated_price": 3000
}
```
**Expected Output:**
- Status Code: `201 Created`
- Response chứa thông tin trứng gà đã tạo

---

## 2. GET - Lấy 2 nguyên liệu theo ID

### Test Case 2.1: Lấy nguyên liệu theo ID (ID = 1)
**Method:** `GET`  
**URL:** `http://localhost:8001/v2/ingredients/1`  
**Body:** Không có  
**Expected Output:**
- Status Code: `200 OK`
- Response body chứa thông tin nguyên liệu với `component_id: 1`
- Bao gồm đầy đủ các trường: `component_id`, `component_name`, `type`, `category`, và các trường dinh dưỡng

---

### Test Case 2.2: Lấy nguyên liệu theo ID (ID = 3)
**Method:** `GET`  
**URL:** `http://localhost:8001/v2/ingredients/3`  
**Body:** Không có  
**Expected Output:**
- Status Code: `200 OK`
- Response body chứa thông tin nguyên liệu với `component_id: 3`
- Đầy đủ thông tin nguyên liệu

---

## 3. GET MANY - Lấy danh sách nguyên liệu (Pagination)

### Test Case 3.1: Lấy trang đầu tiên (5 items)
**Method:** `GET`  
**URL:** `http://localhost:8001/v2/ingredients/?limit=5`  
**Body:** Không có  
**Expected Output:**
- Status Code: `200 OK`
- Response body có dạng:
```json
{
  "data": [
    // 5 nguyên liệu đầu tiên
  ],
  "next_cursor": 5,
  "size": 5
}
```
- `data`: mảng chứa 5 nguyên liệu
- `next_cursor`: ID của nguyên liệu cuối cùng (để dùng cho lần pagination tiếp theo)
- `size`: 5

---

### Test Case 3.2: Lấy trang thứ hai (5 items tiếp theo)
**Method:** `GET`  
**URL:** `http://localhost:8001/v2/ingredients/?cursor=5&limit=5`  
**Body:** Không có  
**Expected Output:**
- Status Code: `200 OK`
- Response body có dạng:
```json
{
  "data": [
    // 5 nguyên liệu tiếp theo (từ ID > 5)
  ],
  "next_cursor": 10,
  "size": 5,
}
```
- `data`: mảng chứa 5 nguyên liệu tiếp theo
- `next_cursor`: ID của nguyên liệu cuối cùng trong trang này
- `size`: 5

---

## 4. SEARCH - Tìm kiếm nguyên liệu

### Test Case 4.1: Tìm kiếm với keyword "thịt"
**Method:** `GET`  
**URL:** `http://localhost:8001/v2/ingredients/search?keyword=thịt&limit=5`  
**Body:** Không có  
**Expected Output:**
- Status Code: `200 OK`
- Response body có dạng:
```json
{
  "data": [
    // Các nguyên liệu có tên chứa "thịt" (ví dụ: "Thịt lợn")
  ],
  "next_cursor": null hoặc số,
  "size": số lượng kết quả
}
```
- `data`: mảng chứa các nguyên liệu có `component_name` chứa keyword "thịt"
- Ít nhất chứa nguyên liệu "Thịt lợn" đã tạo ở Test Case 1.2

---

### Test Case 4.2: Tìm kiếm với keyword "sữa"
**Method:** `GET`  
**URL:** `http://localhost:8001/v2/ingredients/search?keyword=sữa&limit=5`  
**Body:** Không có  
**Expected Output:**
- Status Code: `200 OK`
- Response body có dạng:
```json
{
  "data": [
    // Các nguyên liệu có tên chứa "sữa" (ví dụ: "Sữa tươi")
  ],
  "next_cursor": null hoặc số,
  "size": số lượng kết quả
}
```
- `data`: mảng chứa các nguyên liệu có `component_name` chứa keyword "sữa"
- Ít nhất chứa nguyên liệu "Sữa tươi" đã tạo ở Test Case 1.6

---

## 5. FILTER - Lọc nguyên liệu theo category

### Test Case 5.1: Lọc nguyên liệu category "Rau củ"
**Method:** `GET`  
**URL:** `http://localhost:8001/v2/ingredients/filter?category=Rau củ&limit=5`  
**Body:** Không có  
**Expected Output:**
- Status Code: `200 OK`
- Response body có dạng:
```json
{
  "data": [
    // Các nguyên liệu có category = "Rau củ"
  ],
  "next_cursor": null hoặc số,
  "size": số lượng kết quả
}
```
- `data`: mảng chứa các nguyên liệu có `category: "Rau củ"`
- Ít nhất chứa nguyên liệu "Cà chua" đã tạo ở Test Case 1.1
- Tất cả items trong `data` đều có `category: "Rau củ"`

---

### Test Case 5.2: Lọc nguyên liệu category "Thịt tươi"
**Method:** `GET`  
**URL:** `http://localhost:8001/v2/ingredients/filter?category=Thịt tươi&limit=5`  
**Body:** Không có  
**Expected Output:**
- Status Code: `200 OK`
- Response body có dạng:
```json
{
  "data": [
    // Các nguyên liệu có category = "Thịt tươi"
  ],
  "next_cursor": null hoặc số,
  "size": số lượng kết quả
}
```
- `data`: mảng chứa các nguyên liệu có `category: "Thịt tươi"`
- Ít nhất chứa nguyên liệu "Thịt lợn" đã tạo ở Test Case 1.2
- Tất cả items trong `data` đều có `category: "Thịt tươi"`

---

## 6. UPDATE - Cập nhật nguyên liệu

### Test Case 6.1: Cập nhật nguyên liệu ID = 1 (Cà chua)
**Method:** `PUT`  
**URL:** `http://localhost:8001/v2/ingredients/1`  
**Body:**
```json
{
  "type": "countable_ingredient",
  "component_name": "Cà chua bi",
  "estimated_price": 7000,
  "protein": 1.0
}
```
**Expected Output:**
- Status Code: `200 OK`
- Response body chứa:
  - `component_id`: 1
  - `component_name`: `"Cà chua bi"` (đã được cập nhật)
  - `estimated_price`: 7000 (đã được cập nhật)
  - `protein`: 1.0 (đã được cập nhật)
  - Các trường khác giữ nguyên giá trị cũ

---

### Test Case 6.2: Cập nhật nguyên liệu ID = 6 (Sữa tươi)
**Method:** `PUT`  
**URL:** `http://localhost:8001/v2/ingredients/6`  
**Body:**
```json
{
  "type": "uncountable_ingredient",
  "component_name": "Sữa tươi không đường",
  "estimated_shelf_life": 10,
  "fat": 3.0
}
```
**Expected Output:**
- Status Code: `200 OK`
- Response body chứa:
  - `component_id`: 6
  - `type`: `"uncountable_ingredient"`
  - `component_name`: `"Sữa tươi không đường"` (đã được cập nhật)
  - `estimated_shelf_life`: 10 (đã được cập nhật)
  - `fat`: 3.0 (đã được cập nhật)
  - Các trường khác giữ nguyên

---

### Test Case 6.3: Cập nhật nguyên liệu ID = 2 (Thịt lợn)
**Method:** `PUT`  
**URL:** `http://localhost:8001/v2/ingredients/2`  
**Body:**
```json
{
  "type": "countable_ingredient",
  "estimated_price": 180000,
  "calories": 250
}
```
**Expected Output:**
- Status Code: `200 OK`
- Response body chứa:
  - `component_id`: 2
  - `estimated_price`: 180000 (đã được cập nhật)
  - `calories`: 250 (đã được cập nhật)
  - `component_name`: `"Thịt lợn"` (giữ nguyên)
  - Các trường khác giữ nguyên giá trị cũ

---

## 7. DELETE - Xóa nguyên liệu

### Test Case 7.1: Xóa nguyên liệu ID = 10 (Trứng gà)
**Method:** `DELETE`  
**URL:** `http://localhost:8001/v2/ingredients/10`  
**Body:** Không có  
**Expected Output:**
- Status Code: `204 No Content`
- Response body: Không có (empty body)
- Sau khi xóa, GET `/v2/ingredients/10` sẽ trả về `404 Not Found`

---

## Lưu ý

1. **Thứ tự thực hiện:** Các test case nên được thực hiện theo thứ tự đã liệt kê (Create → Get → Get Many → Search → Filter → Update → Delete)

2. **Component IDs:** Các ID trong test cases (1, 2, 3, 6, 10) giả định rằng các nguyên liệu được tạo theo thứ tự từ Test Case 1.1 đến 1.10. Nếu ID thực tế khác, cần điều chỉnh lại các test case GET, UPDATE, DELETE cho phù hợp.

3. **Pagination cursor:** Giá trị `cursor` trong Test Case 3.2 (cursor=5) giả định rằng 5 items đầu có ID từ 1-5. Cần điều chỉnh dựa trên `next_cursor` thực tế từ Test Case 3.1.

4. **Measurement Units:**
   - Countable: `quả`, `củ`, `gói`, `bó`, `miếng`, `nhánh`, `tép`
   - Uncountable: `G`, `ML`

5. **Categories:** Các category hợp lệ bao gồm: `Rau củ`, `Thịt tươi`, `Hải sản và cá viên`, `Trái cây tươi`, `Gia vị`, `Sữa`, `Lương thực`, `Bánh ngọt`, `Khác`, và các category khác được định nghĩa trong enum.

