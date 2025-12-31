# Test Cases cho Storage API

Base URL: `http://localhost:8002/v1/storages`

**Lưu ý:** Các test case này giả định rằng bạn đã có group_id hợp lệ (ví dụ: group_id = 1).

---

## 1. CREATE - Tạo 2 storage mỗi loại

### Test Case 1.1: Tạo 2 Fridge storage
**Method:** `POST`  
**URL:** `http://localhost:8002/v1/storages/`  
**Body 1:**
```json
{
  "storage_type": "fridge",
  "group_id": 1,
  "storage_name": "Tủ lạnh chính"
}
```

**Body 2:**
```json
{
  "storage_type": "fridge",
  "group_id": 1,
  "storage_name": "Tủ lạnh phụ"
}
```

**Expected Output:**
- Status Code: `201 Created`
- Response body chứa StorageResponse với:
  - `storage_id`: số nguyên (ID được tạo tự động)
  - `storage_name`: tên đã cung cấp hoặc tên tự động nếu không cung cấp
  - `storage_type`: `"fridge"`
  - `group_id`: 1
  - `storable_units`: mảng rỗng `[]`

---

### Test Case 1.2: Tạo 2 Freezer storage
**Method:** `POST`  
**URL:** `http://localhost:8002/v1/storages/`  
**Body 1:**
```json
{
  "storage_type": "freezer",
  "group_id": 1,
  "storage_name": "Tủ đông chính"
}
```

**Body 2:**
```json
{
  "storage_type": "freezer",
  "group_id": 1,
  "storage_name": "Tủ đông phụ"
}
```

**Expected Output:**
- Status Code: `201 Created`
- Response body chứa StorageResponse với:
  - `storage_type`: `"freezer"`
  - Các field khác tương tự Test Case 1.1

---

### Test Case 1.3: Tạo 2 Pantry storage
**Method:** `POST`  
**URL:** `http://localhost:8002/v1/storages/`  
**Body 1:**
```json
{
  "storage_type": "pantry",
  "group_id": 1,
  "storage_name": "Tủ bếp trên"
}
```

**Body 2:**
```json
{
  "storage_type": "pantry",
  "group_id": 1,
  "storage_name": "Tủ bếp dưới"
}
```

**Expected Output:**
- Status Code: `201 Created`
- Response body chứa StorageResponse với:
  - `storage_type`: `"pantry"`
  - Các field khác tương tự Test Case 1.1

---

### Test Case 1.4: Tạo 2 Bulk Storage storage
**Method:** `POST`  
**URL:** `http://localhost:8002/v1/storages/`  
**Body 1:**
```json
{
  "storage_type": "bulk_storage",
  "group_id": 1,
  "storage_name": "Kho lớn 1"
}
```

**Body 2:**
```json
{
  "storage_type": "bulk_storage",
  "group_id": 1,
  "storage_name": "Kho lớn 2"
}
```

**Expected Output:**
- Status Code: `201 Created`
- Response body chứa StorageResponse với:
  - `storage_type`: `"bulk_storage"`
  - Các field khác tương tự Test Case 1.1

---

### Test Case 1.5: Tạo storage không cung cấp tên (tên tự động)
**Method:** `POST`  
**URL:** `http://localhost:8002/v1/storages/`  
**Body:**
```json
{
  "storage_type": "fridge",
  "group_id": 1
}
```

**Expected Output:**
- Status Code: `201 Created`
- Response body chứa StorageResponse với:
  - `storage_name`: tên tự động theo format `"Fridge #<storage_id> of Group #<group_id>"` (ví dụ: `"Fridge #1 of Group #1"`)

---

## 2. GET - Lấy danh sách storages

### Test Case 2.1: Lấy tất cả storages
**Method:** `GET`  
**URL:** `http://localhost:8002/v1/storages/`  
**Query Parameters:** Không có (hoặc `cursor=0&limit=100`)  
**Expected Output:**
- Status Code: `200 OK`
- Response body là PaginationResponse chứa:
  - `data`: mảng các StorageResponse (ít nhất 8 items từ các test case trên)
  - `next_cursor`: cursor cho trang tiếp theo (nếu có)
  - `size`: số lượng items trong response hiện tại
  - `has_more`: boolean cho biết còn items nữa không

---

### Test Case 2.2: Lấy storage theo ID
**Method:** `GET`  
**URL:** `http://localhost:8002/v1/storages/{id}`  
**Note:** Thay `{id}` bằng storage_id từ một trong các storage đã tạo ở Test Case 1.x  
**Expected Output:**
- Status Code: `200 OK`
- Response body là StorageResponse với đầy đủ thông tin của storage đó

---

## 3. UPDATE - Cập nhật storage

### Test Case 3.1: Update đổi tên và type của một storage
**Method:** `PUT`  
**URL:** `http://localhost:8002/v1/storages/{id}`  
**Note:** Chọn một storage_id từ các storage đã tạo (ví dụ: storage đầu tiên từ Test Case 1.1)  
**Body:**
```json
{
  "storage_name": "Tủ lạnh đã đổi tên",
  "storage_type": "freezer"
}
```

**Expected Output:**
- Status Code: `200 OK`
- Response body là StorageResponse với:
  - `storage_id`: giữ nguyên (cùng ID)
  - `storage_name`: `"Tủ lạnh đã đổi tên"` (đã được cập nhật)
  - `storage_type`: `"freezer"` (đã được cập nhật từ `"fridge"`)
  - `group_id`: giữ nguyên
  - `storable_units`: giữ nguyên (nếu có)

---

### Test Case 3.2: Update chỉ đổi tên
**Method:** `PUT`  
**URL:** `http://localhost:8002/v1/storages/{id}`  
**Note:** Chọn một storage_id khác  
**Body:**
```json
{
  "storage_name": "Tên mới chỉ đổi tên"
}
```

**Expected Output:**
- Status Code: `200 OK`
- Response body là StorageResponse với:
  - `storage_name`: `"Tên mới chỉ đổi tên"` (đã được cập nhật)
  - `storage_type`: giữ nguyên (không thay đổi)
  - Các field khác giữ nguyên

---

### Test Case 3.3: Update chỉ đổi type
**Method:** `PUT`  
**URL:** `http://localhost:8002/v1/storages/{id}`  
**Note:** Chọn một storage_id khác  
**Body:**
```json
{
  "storage_type": "pantry"
}
```

**Expected Output:**
- Status Code: `200 OK`
- Response body là StorageResponse với:
  - `storage_type`: `"pantry"` (đã được cập nhật)
  - `storage_name`: giữ nguyên (không thay đổi)
  - Các field khác giữ nguyên

---

## 4. DELETE - Xóa storage

### Test Case 4.1: Xóa một storage
**Method:** `DELETE`  
**URL:** `http://localhost:8002/v1/storages/{id}`  
**Note:** Chọn một storage_id từ các storage đã tạo (ví dụ: storage thứ hai từ Test Case 1.1)  
**Expected Output:**
- Status Code: `204 No Content`
- Response body: rỗng

---

### Test Case 4.2: Verify storage đã bị xóa
**Method:** `GET`  
**URL:** `http://localhost:8002/v1/storages/{id}`  
**Note:** Sử dụng cùng storage_id đã xóa ở Test Case 4.1  
**Expected Output:**
- Status Code: `404 Not Found`
- Response body:
```json
{
  "detail": "Storage with id={id} not found"
}
```

---

## 5. Verification - Xác nhận kết quả cuối cùng

### Test Case 5.1: Lấy danh sách storages sau khi update và delete
**Method:** `GET`  
**URL:** `http://localhost:8002/v1/storages/`  
**Expected Output:**
- Status Code: `200 OK`
- Response body chứa ít nhất 7 storages (8 tạo ban đầu - 1 đã xóa)
- Một trong các storage phải có:
  - `storage_name`: `"Tủ lạnh đã đổi tên"`
  - `storage_type`: `"freezer"` (đã được update từ `"fridge"`)

---

## Lưu ý

1. **Thứ tự thực hiện:**
   - Chạy các Test Case 1.x để tạo 8 storages (2 mỗi loại)
   - Chạy Test Case 2.1 hoặc 2.2 để verify các storages đã được tạo
   - Chạy Test Case 3.1 để update tên và type của một storage
   - Chạy Test Case 4.1 để xóa một storage
   - Chạy Test Case 5.1 để verify kết quả cuối cùng

2. **StorageType values:**
   - `"fridge"` (Tủ lạnh)
   - `"freezer"` (Tủ đông)
   - `"pantry"` (Tủ bếp)
   - `"bulk_storage"` (Kho lớn)

3. **Storage Name:**
   - Nếu không cung cấp `storage_name`, hệ thống sẽ tự động tạo tên theo format: `"{StorageType} #{storage_id} of Group #{group_id}"`
   - Ví dụ: `"Fridge #1 of Group #1"`, `"Freezer #2 of Group #1"`

4. **Update:**
   - Có thể update chỉ `storage_name`, chỉ `storage_type`, hoặc cả hai
   - Các field không được cung cấp trong body sẽ giữ nguyên giá trị cũ

5. **Delete:**
   - Khi xóa storage, tất cả `storable_units` liên quan cũng sẽ bị xóa (cascade delete)
   - Sau khi xóa, không thể truy cập storage đó nữa (404 Not Found)

6. **Pagination:**
   - Endpoint GET `/` hỗ trợ pagination với `cursor` và `limit`
   - `cursor`: ID của item cuối cùng từ request trước (optional)
   - `limit`: Số lượng items muốn lấy (default: 100, min: 1)

7. **Verification:**
   - Sau mỗi thao tác (create, update, delete), nên thực hiện GET để xác nhận dữ liệu đã được thay đổi đúng
   - Storage ID sẽ giữ nguyên khi update, chỉ thay đổi khi tạo mới

