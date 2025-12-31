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

---

## 6. CREATE - Thêm Storable Units vào Storage

**Lưu ý:** Các test case này giả định rằng bạn đã tạo storage với `storage_id = 1` từ các test case trước.

Base URL: `http://localhost:8002/v1/storable_units`

---

### Test Case 6.1: Thêm unit cà chua bi (countable ingredient)
**Method:** `POST`  
**URL:** `http://localhost:8002/v1/storable_units/`  
**Body:**
```json
{
  "unit_name": "Cà chua bi",
  "storage_id": 1,
  "package_quantity": 15,
  "component_id": 1,
  "content_type": "countable_ingredient"
}
```

**Expected Output:**
- Status Code: `201 Created`
- Response body chứa StorableUnitResponse với:
  - `unit_id`: số nguyên (ID được tạo tự động)
  - `unit_name`: `"Cà chua bi"`
  - `storage_id`: 1
  - `package_quantity`: 15
  - `component_id`: 1
  - `content_type`: `"countable_ingredient"`
  - `content_quantity`: `null`
  - `content_unit`: `null`
  - `added_date`: timestamp hiện tại
  - `expiration_date`: `null` (nếu không cung cấp)

---

### Test Case 6.2: Thêm unit sữa tươi 200ml (uncountable ingredient)
**Method:** `POST`  
**URL:** `http://localhost:8002/v1/storable_units/`  
**Body:**
```json
{
  "unit_name": "Sữa tươi 200ml",
  "storage_id": 1,
  "package_quantity": 4,
  "component_id": 7,
  "content_type": "uncountable_ingredient",
  "content_quantity": 800.0,
  "content_unit": "ML"
}
```

**Expected Output:**
- Status Code: `201 Created`
- Response body chứa StorableUnitResponse với:
  - `unit_name`: `"Sữa tươi 200ml"`
  - `storage_id`: 1
  - `package_quantity`: 4
  - `component_id`: 7
  - `content_type`: `"uncountable_ingredient"`
  - `content_quantity`: 800.0 (4 hộp × 200ml = 800ml)
  - `content_unit`: `"ML"`

---

### Test Case 6.3: Thêm unit sữa tươi 1000ml (uncountable ingredient)
**Method:** `POST`  
**URL:** `http://localhost:8002/v1/storable_units/`  
**Body:**
```json
{
  "unit_name": "Sữa tươi 1000ml",
  "storage_id": 1,
  "package_quantity": 2,
  "component_id": 7,
  "content_type": "uncountable_ingredient",
  "content_quantity": 2000.0,
  "content_unit": "ML"
}
```

**Expected Output:**
- Status Code: `201 Created`
- Response body chứa StorableUnitResponse với:
  - `unit_name`: `"Sữa tươi 1000ml"`
  - `storage_id`: 1
  - `package_quantity`: 2
  - `component_id`: 7
  - `content_type`: `"uncountable_ingredient"`
  - `content_quantity`: 2000.0 (2 hộp × 1000ml = 2000ml)
  - `content_unit`: `"ML"`

---

### Test Case 6.4: Thêm unit không có component_id (bún đậu mắm tôm)
**Method:** `POST`  
**URL:** `http://localhost:8002/v1/storable_units/`  
**Body:**
```json
{
  "unit_name": "Bún đậu mắm tôm",
  "storage_id": 1,
  "package_quantity": 1
}
```

**Expected Output:**
- Status Code: `201 Created`
- Response body chứa StorableUnitResponse với:
  - `unit_name`: `"Bún đậu mắm tôm"`
  - `storage_id`: 1
  - `package_quantity`: 1
  - `component_id`: `null`
  - `content_type`: `null`
  - `content_quantity`: `null`
  - `content_unit`: `null`

---

### Test Case 6.5: Verify các units đã được thêm vào storage
**Method:** `GET`  
**URL:** `http://localhost:8002/v1/storages/1`  
**Expected Output:**
- Status Code: `200 OK`
- Response body là StorageResponse với:
  - `storage_id`: 1
  - `storable_units`: mảng chứa ít nhất 4 StorableUnitResponse:
    - 1 unit với `unit_name`: `"Cà chua bi"`, `component_id`: 1, `package_quantity`: 15
    - 1 unit với `unit_name`: `"Sữa tươi 200ml"`, `component_id`: 7, `content_quantity`: 800.0
    - 1 unit với `unit_name`: `"Sữa tươi 1000ml"`, `component_id`: 7, `content_quantity`: 2000.0
    - 1 unit với `unit_name`: `"Bún đậu mắm tôm"`, `component_id`: `null`

---

### Test Case 6.6: Lấy danh sách storable units theo storage_id
**Method:** `GET`  
**URL:** `http://localhost:8002/v1/storable_units/filter?storage_id=1`  
**Expected Output:**
- Status Code: `200 OK`
- Response body là PaginationResponse chứa:
  - `data`: mảng các StorableUnitResponse (ít nhất 4 items)
  - `size`: số lượng units trong storage_id = 1
  - `has_more`: boolean

---

## Lưu ý về Storable Units

1. **Content Type:**
   - `"countable_ingredient"`: Dùng cho các nguyên liệu đếm được (ví dụ: quả, cái)
     - `content_quantity` và `content_unit` phải là `null`
     - Số lượng được thể hiện qua `package_quantity`
   - `"uncountable_ingredient"`: Dùng cho các nguyên liệu đo lường được (ví dụ: ml, g)
     - `content_quantity` và `content_unit` phải được cung cấp
     - `content_unit` có thể là `"G"` (gram) hoặc `"ML"` (milliliter)

2. **Component ID và Content Type:**
   - Nếu có `component_id`, phải có `content_type`
   - Nếu không có `component_id`, không được có `content_type`
   - Đây là constraint của database để đảm bảo tính nhất quán

3. **Package Quantity:**
   - Mặc định là 1 nếu không cung cấp
   - Phải >= 1
   - Đại diện cho số lượng package/unit (ví dụ: 15 quả, 4 hộp, 2 hộp)

4. **Content Quantity:**
   - Chỉ cần thiết khi `content_type = "uncountable_ingredient"`
   - Phải > 0 nếu được cung cấp
   - Đại diện cho tổng số lượng đo lường (ví dụ: 800ml = 4 hộp × 200ml)

5. **Verification:**
   - Sau khi thêm units, có thể verify bằng cách:
     - GET storage theo ID để xem danh sách `storable_units`
     - GET `/v1/storable_units/filter?storage_id={id}` để lấy danh sách units trong storage
     - GET `/v1/storable_units/{unit_id}` để lấy thông tin chi tiết một unit

---

## 7. CONSUME - Tiêu thụ Storable Unit

**Lưu ý:** Các test case này giả định rằng bạn đã có storable unit với `unit_id = 6` từ các test case trước.

Base URL: `http://localhost:8002/v1/storable_units`

---

### Test Case 7.1: Consume số lượng 1 cho unit có id=6
**Method:** `POST`  
**URL:** `http://localhost:8002/v1/storable_units/6/consume?consume_quantity=1`  
**Body:** Không có (empty body)

**Expected Output:**
- Status Code: `200 OK`
- Response body là GenericResponse với:
  - `message`: `"Consumed"` (nếu unit còn lại sau khi consume) hoặc `"Consumed and deleted"` (nếu unit đã hết và bị xóa)
  - `data`: 
    - Nếu unit còn lại: StorableUnitResponse với `package_quantity` đã giảm đi 1
    - Nếu unit đã hết: `null` (unit đã bị xóa)

**Ví dụ Response (nếu unit còn lại):**
```json
{
  "message": "Consumed",
  "data": {
    "unit_id": 6,
    "unit_name": "...",
    "storage_id": 1,
    "package_quantity": <giá_trị_cũ - 1>,
    ...
  }
}
```

**Ví dụ Response (nếu unit đã hết):**
```json
{
  "message": "Consumed and deleted",
  "data": null
}
```

---

### Test Case 7.2: Verify unit đã được consume
**Method:** `GET`  
**URL:** `http://localhost:8002/v1/storable_units/6`  
**Expected Output:**
- Nếu unit còn lại sau khi consume:
  - Status Code: `200 OK`
  - Response body là StorableUnitResponse với `package_quantity` đã giảm đi 1 so với ban đầu
- Nếu unit đã hết và bị xóa:
  - Status Code: `404 Not Found`
  - Response body:
  ```json
  {
    "detail": "StorableUnit with id=6 not found"
  }
  ```

---

### Test Case 7.3: Consume với số lượng vượt quá (error case)
**Method:** `POST`  
**URL:** `http://localhost:8002/v1/storable_units/6/consume?consume_quantity=999999`  
**Note:** Sử dụng số lượng lớn hơn `package_quantity` hiện tại của unit.  
**Body:** Không có (empty body)

**Expected Output:**
- Status Code: `400 Bad Request`
- Response body:
```json
{
  "detail": "Cannot consume from StorableUnit with id=6: insufficient quantity (available: <số_lượng_còn_lại>, requested: 999999)"
}
```

---

### Test Case 7.4: Consume unit không tồn tại (error case)
**Method:** `POST`  
**URL:** `http://localhost:8002/v1/storable_units/99999/consume?consume_quantity=1`  
**Body:** Không có (empty body)

**Expected Output:**
- Status Code: `404 Not Found`
- Response body:
```json
{
  "detail": "StorableUnit with id=99999 not found"
}
```

---

## Lưu ý về Consume

1. **Consume Quantity:**
   - Phải là số nguyên > 0
   - Không thể consume nhiều hơn `package_quantity` hiện có
   - Nếu consume bằng `package_quantity`, unit sẽ bị xóa

2. **Response:**
   - Nếu unit còn lại: trả về unit đã được cập nhật với `package_quantity` mới
   - Nếu unit đã hết: trả về `null` và unit bị xóa khỏi database

3. **Background Tasks:**
   - Khi unit bị xóa (consume hết), hệ thống sẽ publish component existence update event
   - Điều này giúp các service khác biết về sự thay đổi trong kho

4. **Verification:**
   - Sau khi consume, nên verify bằng cách GET unit theo ID
   - Nếu unit đã bị xóa, sẽ nhận được 404 Not Found
   - Có thể kiểm tra storage để xem unit đã bị xóa khỏi danh sách `storable_units`


