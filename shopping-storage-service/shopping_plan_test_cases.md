# Test Cases cho Shopping Plan API

Base URL: `http://localhost:8002/v1/shopping_plans`

**Lưu ý:** Các test case này giả định rằng bạn đã có:
- `group_id = 1`
- `assigner_id = 1` (người tạo plan)
- `assignee_id = 2` (người được giao plan)
- Storage với `storage_id = 1` (đã tạo từ các test case trước)
- Component IDs: 1 (cà chua bi), 7 (sữa tươi)

---

## 1. CREATE - Tạo Shopping Plan

### Test Case 1.1: Tạo shopping plan với countable và uncountable ingredients
**Method:** `POST`  
**URL:** `http://localhost:8002/v1/shopping_plans/`  
**Body:**
```json
{
  "group_id": 1,
  "deadline": "2025-12-31T23:59:59",
  "assigner_id": 1,
  "shopping_list": [
    {
      "type": "countable_ingredient",
      "unit": "quả",
      "quantity": 20,
      "component_id": 1,
      "component_name": "Cà chua bi"
    },
    {
      "type": "uncountable_ingredient",
      "unit": "ML",
      "quantity": 1000,
      "component_id": 7,
      "component_name": "Sữa tươi"
    }
  ],
  "others": {
    "note": "Mua thêm đồ uống nếu có"
  }
}
```

**Expected Output:**
- Status Code: `201 Created`
- Response body là PlanResponse với:
  - `plan_id`: số nguyên (ID được tạo tự động)
  - `group_id`: 1
  - `deadline`: `"2025-12-31T23:59:59"`
  - `assigner_id`: 1
  - `assignee_id`: `null` (chưa được assign)
  - `plan_status`: `"created"`
  - `shopping_list`: mảng chứa 2 items như đã tạo
  - `others`: object chứa note
  - `last_modified`: timestamp hiện tại

---

## 2. ASSIGN - Gán plan cho người thực hiện

### Test Case 2.1: Assign plan thành công
**Method:** `POST`  
**URL:** `http://localhost:8002/v1/shopping_plans/{plan_id}/assign?assignee_id=2`  
**Note:** Thay `{plan_id}` bằng plan_id từ Test Case 1.1  
**Body:** Không có (empty body)

**Expected Output:**
- Status Code: `200 OK`
- Response body là PlanResponse với:
  - `plan_status`: `"in_progress"` (đã thay đổi từ `"created"`)
  - `assignee_id`: 2 (đã được gán)
  - Các field khác giữ nguyên

---

### Test Case 2.2: Assign plan với status không hợp lệ (error case)
**Method:** `POST`  
**URL:** `http://localhost:8002/v1/shopping_plans/{plan_id}/assign?assignee_id=3`  
**Note:** Sử dụng cùng plan_id đã được assign ở Test Case 2.1  
**Body:** Không có (empty body)

**Expected Output:**
- Status Code: `400 Bad Request`
- Response body:
```json
{
  "detail": "Operation not allowed: plan status must be created, got in_progress"
}
```

---

## 3. REPORT - Báo cáo hoàn thành plan

### Test Case 3.1: Report với confirm=True (thành công - không validate)
**Method:** `POST`  
**URL:** `http://localhost:8002/v1/shopping_plans/{plan_id}/report?assignee_id=2&confirm=true`  
**Note:** Sử dụng plan_id từ Test Case 2.1  
**Body:**
```json
{
  "plan_id": <plan_id>,
  "report_content": [
    {
      "storage_id": 1,
      "package_quantity": 15,
      "unit_name": "Cà chua bi",
      "component_id": 1,
      "content_type": "countable_ingredient"
    },
    {
      "storage_id": 1,
      "package_quantity": 2,
      "unit_name": "Sữa tươi 500ml",
      "component_id": 7,
      "content_type": "uncountable_ingredient",
      "content_quantity": 1000.0,
      "content_unit": "ML"
    }
  ],
  "spent_amount": 50000
}
```

**Expected Output:**
- Status Code: `200 OK`
- Response body là GenericResponse với:
  - `message`: `"Report accepted and plan completed"`
  - `data`: PlanResponse với `plan_status`: `"completed"`
- **Lưu ý:** Các items trong `report_content` sẽ được thêm vào storage như StorableUnits (background task)

---

### Test Case 3.2: Report với confirm=False và đủ items (thành công - có validate)
**Method:** `POST`  
**URL:** `http://localhost:8002/v1/shopping_plans/{plan_id}/report?assignee_id=2&confirm=false`  
**Note:** Tạo plan mới, assign, và report với đủ items  
**Body:**
```json
{
  "plan_id": <plan_id>,
  "report_content": [
    {
      "storage_id": 1,
      "package_quantity": 20,
      "unit_name": "Cà chua bi",
      "component_id": 1,
      "content_type": "countable_ingredient"
    },
    {
      "storage_id": 1,
      "package_quantity": 1,
      "unit_name": "Sữa tươi 1000ml",
      "component_id": 7,
      "content_type": "uncountable_ingredient",
      "content_quantity": 1000.0,
      "content_unit": "ML"
    }
  ],
  "spent_amount": 60000
}
```

**Expected Output:**
- Status Code: `200 OK`
- Response body là GenericResponse với:
  - `message`: `"Report accepted and plan completed"`
  - `data`: PlanResponse với `plan_status`: `"completed"`

---

### Test Case 3.3: Report với confirm=False và thiếu items (thất bại)
**Method:** `POST`  
**URL:** `http://localhost:8002/v1/shopping_plans/{plan_id}/report?assignee_id=2&confirm=false`  
**Note:** Tạo plan mới với yêu cầu 20 quả cà chua bi và 1000ml sữa, nhưng chỉ report 10 quả và 500ml  
**Body:**
```json
{
  "plan_id": <plan_id>,
  "report_content": [
    {
      "storage_id": 1,
      "package_quantity": 10,
      "unit_name": "Cà chua bi",
      "component_id": 1,
      "content_type": "countable_ingredient"
    },
    {
      "storage_id": 1,
      "package_quantity": 1,
      "unit_name": "Sữa tươi 500ml",
      "component_id": 7,
      "content_type": "uncountable_ingredient",
      "content_quantity": 500.0,
      "content_unit": "ML"
    }
  ],
  "spent_amount": 30000
}
```

**Expected Output:**
- Status Code: `200 OK`
- Response body là GenericResponse với:
  - `message`: `"Report incomplete"`
  - `data`: object chứa `missing_items`:
    ```json
    {
      "missing_items": [
        {
          "component_id": 1,
          "component_name": "Cà chua bi",
          "missing_quantity": 10
        },
        {
          "component_id": 7,
          "component_name": "Sữa tươi",
          "missing_quantity": 500
        }
      ]
    }
    ```
- Plan status vẫn là `"in_progress"` (chưa completed)

---

### Test Case 3.4: Report với assignee_id sai (thất bại)
**Method:** `POST`  
**URL:** `http://localhost:8002/v1/shopping_plans/{plan_id}/report?assignee_id=999&confirm=true`  
**Note:** Sử dụng plan đã được assign cho assignee_id = 2, nhưng report với assignee_id = 999  
**Body:**
```json
{
  "plan_id": <plan_id>,
  "report_content": [
    {
      "storage_id": 1,
      "package_quantity": 20,
      "unit_name": "Cà chua bi",
      "component_id": 1,
      "content_type": "countable_ingredient"
    }
  ],
  "spent_amount": 50000
}
```

**Expected Output:**
- Status Code: `403 Forbidden`
- Response body:
```json
{
  "detail": "Operation not allowed: user 999 is not the current assignee of this plan"
}
```

---

### Test Case 3.5: Report plan với status không hợp lệ (error case)
**Method:** `POST`  
**URL:** `http://localhost:8002/v1/shopping_plans/{plan_id}/report?assignee_id=2&confirm=true`  
**Note:** Sử dụng plan đã completed hoặc cancelled  
**Body:**
```json
{
  "plan_id": <plan_id>,
  "report_content": [],
  "spent_amount": 0
}
```

**Expected Output:**
- Status Code: `400 Bad Request`
- Response body:
```json
{
  "detail": "Operation not allowed: plan status must be in_progress, got completed"
}
```

---

## 4. CANCEL - Hủy plan

### Test Case 4.1: Cancel plan thành công
**Method:** `POST`  
**URL:** `http://localhost:8002/v1/shopping_plans/{plan_id}/cancel?assigner_id=1`  
**Note:** Tạo plan mới, assign, sau đó cancel  
**Body:** Không có (empty body)

**Expected Output:**
- Status Code: `200 OK`
- Response body là PlanResponse với:
  - `plan_status`: `"cancelled"`
  - `assignee_id`: `null` (đã bị xóa)

---

### Test Case 4.2: Cancel plan với assigner_id sai (thất bại)
**Method:** `POST`  
**URL:** `http://localhost:8002/v1/shopping_plans/{plan_id}/cancel?assigner_id=999`  
**Note:** Sử dụng plan được tạo bởi assigner_id = 1, nhưng cancel với assigner_id = 999  
**Body:** Không có (empty body)

**Expected Output:**
- Status Code: `403 Forbidden`
- Response body:
```json
{
  "detail": "Operation not allowed: user 999 is not the assigner of this plan"
}
```

---

## 5. REOPEN - Mở lại plan đã hủy

### Test Case 5.1: Reopen plan thành công
**Method:** `POST`  
**URL:** `http://localhost:8002/v1/shopping_plans/{plan_id}/reopen?assigner_id=1`  
**Note:** Sử dụng plan đã bị cancel ở Test Case 4.1  
**Body:** Không có (empty body)

**Expected Output:**
- Status Code: `200 OK`
- Response body là PlanResponse với:
  - `plan_status`: `"created"` (đã được mở lại)

---

## 6. VERIFICATION - Xác nhận report và storable units

### Test Case 6.1: Verify storable units đã được thêm sau khi report
**Method:** `GET`  
**URL:** `http://localhost:8002/v1/storages/1`  
**Note:** Sau khi report plan thành công (Test Case 3.1 hoặc 3.2)  
**Expected Output:**
- Status Code: `200 OK`
- Response body là StorageResponse với:
  - `storable_units`: mảng chứa các units đã được thêm từ report:
    - Unit với `unit_name`: `"Cà chua bi"`, `component_id`: 1, `package_quantity`: 15 (hoặc 20)
    - Unit với `unit_name`: `"Sữa tươi 500ml"` (hoặc tương tự), `component_id`: 7, `content_quantity`: 1000.0

---

### Test Case 6.2: Lấy danh sách plans đã completed
**Method:** `GET`  
**URL:** `http://localhost:8002/v1/shopping_plans/filter?plan_status=completed&group_id=1`  
**Expected Output:**
- Status Code: `200 OK`
- Response body là PaginationResponse chứa:
  - `data`: mảng các PlanResponse với `plan_status`: `"completed"`
  - Ít nhất 1 plan từ các test case report thành công

---

### Test Case 6.3: Lấy plan theo ID và verify report
**Method:** `GET`  
**URL:** `http://localhost:8002/v1/shopping_plans/{plan_id}`  
**Note:** Sử dụng plan_id đã completed từ Test Case 3.1 hoặc 3.2  
**Expected Output:**
- Status Code: `200 OK`
- Response body là PlanResponse với:
  - `plan_status`: `"completed"`
  - `assignee_id`: 2
  - `shopping_list`: danh sách items ban đầu

---

## Lưu ý về Shopping Plan

1. **Plan Status Flow:**
   - `CREATED` → `IN_PROGRESS` (khi assign)
   - `IN_PROGRESS` → `COMPLETED` (khi report thành công)
   - `IN_PROGRESS` → `CREATED` (khi unassign)
   - `CREATED` hoặc `IN_PROGRESS` → `CANCELLED` (khi cancel)
   - `CANCELLED` → `CREATED` (khi reopen)

2. **Report với confirm:**
   - `confirm=True`: Bỏ qua validation, hoàn thành plan ngay lập tức
   - `confirm=False`: Validate report content với shopping_list, chỉ complete nếu đủ items

3. **Report Content Validation:**
   - Khi `confirm=False`, hệ thống sẽ kiểm tra:
     - Tổng số lượng reported cho mỗi component_id phải >= số lượng yêu cầu trong shopping_list
     - Với countable: so sánh `package_quantity`
     - Với uncountable: so sánh `package_quantity × content_quantity`

4. **Background Tasks:**
   - Sau khi report thành công, các items trong `report_content` sẽ được thêm vào storage như StorableUnits
   - Quá trình này chạy trong background, có thể mất một chút thời gian

5. **Authorization:**
   - Chỉ assignee có thể report plan
   - Chỉ assigner có thể cancel hoặc reopen plan
   - Các operation sẽ kiểm tra status và authorization trước khi thực hiện

6. **Shopping List Format:**
   - `type`: `"countable_ingredient"` hoặc `"uncountable_ingredient"`
   - `unit`: đơn vị (ví dụ: "quả", "ML", "G")
   - `quantity`: số lượng yêu cầu
   - `component_id`: ID của component/ingredient
   - `component_name`: tên của component

7. **Report Content Format:**
   - Phải khớp với format của StorableUnitCreate
   - Nếu có `component_id`, phải có `content_type`
   - Với `countable_ingredient`: không có `content_quantity` và `content_unit`
   - Với `uncountable_ingredient`: phải có `content_quantity` và `content_unit`

