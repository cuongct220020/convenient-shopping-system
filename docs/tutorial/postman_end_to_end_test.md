# Postman E2E Test (User/Group/Plan/Notifications)

### Chuẩn bị (Postman Environment Variables)

- **BASE_URL**: Gateway URL
  - Nếu chạy qua Kong local: `http://localhost:8000`
  - Nếu chạy compose prod và có redirect HTTPS: `https://localhost` (Postman có thể cần tắt verify SSL certificate)
- **ACCESS_TOKEN**: sẽ set sau khi login
- **USER_ID**: sẽ lấy từ response register
- **GROUP_ID**: sẽ lấy từ response create group
- **PLAN_ID**: sẽ lấy từ response create plan
- **NEW_USER_ID**: `6d054f02-4691-4bb6-8837-1a7d080de6f7` (user thêm vào group để test add/remove)
- **NEW_USER_IDENTIFIER**: username/email của user `NEW_USER_ID` (dùng cho API add member)
- **NOTIFICATION_ID**: set thủ công từ response ở bước 13 (dùng cho bước 14/15)

Header chuẩn cho các API protected:
- **Authorization**: `Bearer {{ACCESS_TOKEN}}`

---

### 1) Register user (username `thanh`, password `12345678`)

**Request**
- **Method**: `POST`
- **URL**: `{{BASE_URL}}/api/v1/user-service/auth/register`
- **Body (JSON)**:

```json
{
  "username": "thanh",
  "email": "thanh@example.com",
  "password": "12345678",
  "first_name": "Thanh",
  "last_name": "Test"
}
```

**Ghi chú**
- Password `12345678` đã đạt yêu cầu **min_length = 8**.

**Lấy USER_ID**
- Trong response, lấy `data.user_id` và set vào env `USER_ID`.

---

### 2) (Nếu cần) Request OTP + Verify OTP để activate account

Nếu login bị báo account chưa active, làm 2 bước sau.

#### 2.1 Request OTP

**Request**
- **Method**: `POST`
- **URL**: `{{BASE_URL}}/api/v1/user-service/auth/otp/send`
- **Body (JSON)**:

```json
{
  "email": "thanh@example.com",
  "action": "register"
}
```

**Tip**
- Nếu service đang chạy DEBUG, response sẽ có `data.otp_code`.

#### 2.2 Verify OTP

**Request**
- **Method**: `POST`
- **URL**: `{{BASE_URL}}/api/v1/user-service/auth/otp/verify`
- **Body (JSON)**:

```json
{
  "email": "thanh@example.com",
  "otp_code": "000000"
}
```

Thay `otp_code` bằng giá trị OTP thật (từ email hoặc từ response nếu DEBUG).

---

### 3) Login

**Request**
- **Method**: `POST`
- **URL**: `{{BASE_URL}}/api/v1/user-service/auth/login`
- **Body (JSON)**:

```json
{
  "identifier": "thanh",
  "password": "12345678"
}
```

**Set ACCESS_TOKEN**
- Lấy `data.access_token` và set vào env `ACCESS_TOKEN`.

---

### 4) Kết nối WebSocket notifications (user channel)

Mở một **WebSocket Request** trong Postman:
- **URL**: `ws://localhost:8000/ws/v2/notification-service/notifications/users/{{USER_ID}}`
  - Nếu bạn dùng `https://localhost` cho API thì WS tương ứng là `wss://localhost/ws/v2/notification-service/notifications/users/{{USER_ID}}`
- **Headers**:
  - `Authorization: Bearer {{ACCESS_TOKEN}}`

Giữ connection này mở để quan sát notification realtime khi assign/report plan.

---

### 5) Create group

**Request**
- **Method**: `POST`
- **URL**: `{{BASE_URL}}/api/v1/user-service/groups/`
- **Headers**: `Authorization: Bearer {{ACCESS_TOKEN}}`
- **Body (JSON)**:

```json
{
  "group_name": "group-thanh",
  "group_avatar_url": null
}
```

**Set GROUP_ID**
- Lấy `data.id` (group id) từ response và set vào env `GROUP_ID`.

---

### 6) Get meals hôm nay

**Request**
- **Method**: `GET`
- **URL**: `{{BASE_URL}}/v1/meals/?meal_date=2026-01-12&group_id={{GROUP_ID}}`
- **Headers**: `Authorization: Bearer {{ACCESS_TOKEN}}`

Ghi chú:
- `meal_date` là format `YYYY-MM-DD`.
- Nếu muốn lọc 1 bữa cụ thể, thêm `&meal_type=dinner` (hoặc `breakfast`, `lunch`).

---

### 7) Command dinner tối nay (recipe id 430 “thịt lợn kho tàu”, 1 servings)

**Request**
- **Method**: `POST`
- **URL**: `{{BASE_URL}}/v1/meals/command?group_id={{GROUP_ID}}`
- **Headers**: `Authorization: Bearer {{ACCESS_TOKEN}}`
- **Body (JSON)**:

```json
{
  "date": "2026-01-12",
  "group_id": "{{GROUP_ID}}",
  "breakfast": { "action": "skip" },
  "lunch": { "action": "skip" },
  "dinner": {
    "action": "upsert",
    "recipe_list": [
      { "recipe_id": 430, "recipe_name": "thịt lợn kho tàu", "servings": 1 }
    ]
  }
}
```

---

### 8) Create shopping plan

**Request**
- **Method**: `POST`
- **URL**: `{{BASE_URL}}/v1/shopping_plans/`
- **Headers**: `Authorization: Bearer {{ACCESS_TOKEN}}`
- **Body (JSON)**:

```json
{
  "group_id": "{{GROUP_ID}}",
  "deadline": "2026-01-13T12:00:00",
  "assigner_id": "{{USER_ID}}",
  "shopping_list": [
    {
      "type": "countable_ingredient",
      "unit": "quả",
      "quantity": 2,
      "component_id": 298,
      "component_name": "cà chua"
    }
  ],
  "others": {}
}
```

**Set PLAN_ID**
- Lấy `plan_id` từ response và set vào env `PLAN_ID`.

---

### 9) Assign plan

**Request**
- **Method**: `POST`
- **URL**: `{{BASE_URL}}/v1/shopping_plans/{{PLAN_ID}}/assign?assignee_id={{USER_ID}}&assignee_username=thanh`
- **Headers**: `Authorization: Bearer {{ACCESS_TOKEN}}`

Kỳ vọng:
- plan status chuyển sang `IN_PROGRESS`
- `notification-service` sẽ tạo notification `plan_assigned` và push ra WebSocket (nếu đang mở WS ở bước 4)

---

### 10) Report plan (report_content rỗng, confirm=true)

**Request**
- **Method**: `POST`
- **URL**: `{{BASE_URL}}/v1/shopping_plans/{{PLAN_ID}}/report?assignee_id={{USER_ID}}&assignee_username=thanh&confirm=true`
- **Headers**: `Authorization: Bearer {{ACCESS_TOKEN}}`
- **Body (JSON)**:

```json
{
  "plan_id": {{PLAN_ID}},
  "report_content": [],
  "spent_amount": 0
}
```

Kỳ vọng:
- plan status chuyển sang `COMPLETED`
- `notification-service` sẽ tạo notification `plan_reported` và push ra WebSocket

---

### 11) Add user `{{NEW_USER_ID}}` vào group hiện tại (để test add/remove)

**Request**
- **Method**: `POST`
- **URL**: `{{BASE_URL}}/api/v1/user-service/groups/{{GROUP_ID}}/members`
- **Headers**: `Authorization: Bearer {{ACCESS_TOKEN}}`
- **Body (JSON)**:

```json
{
  "identifier": "{{NEW_USER_IDENTIFIER}}"
}
```

Kỳ vọng:
- 201 Created nếu add thành công.
- 409 nếu user đã là member.
- 404 nếu identifier không tồn tại.

---

### 12) Xóa user `{{NEW_USER_ID}}` khỏi group hiện tại

**Request**
- **Method**: `DELETE`
- **URL**: `{{BASE_URL}}/api/v1/user-service/groups/{{GROUP_ID}}/members/{{NEW_USER_ID}}`
- **Headers**: `Authorization: Bearer {{ACCESS_TOKEN}}`

Kỳ vọng:
- 200 OK nếu remove thành công.
- 404 nếu không có membership.

Ghi chú:
- Notification realtime (group_user_removed) sẽ được gửi cho **user bị xóa** (tức `{{NEW_USER_ID}}`). Muốn quan sát, cần login user đó và mở thêm WS:
  - `ws://localhost:8000/ws/v2/notification-service/notifications/users/{{NEW_USER_ID}}`

---

### 13) Get notification list (REST)

**Request**
- **Method**: `GET`
- **URL**: `{{BASE_URL}}/api/v2/notification-service/notifications/users/{{USER_ID}}`
- **Headers**: `Authorization: Bearer {{ACCESS_TOKEN}}`

Ghi chú (đường dẫn chuẩn):
- **Qua Kong (gateway)**: `{{BASE_URL}}/api/v2/notification-service/notifications/users/{{USER_ID}}`
- **Gọi thẳng service** (nếu chạy direct): `http://localhost:9005/api/v2/notification-service/notifications/users/{{USER_ID}}`

Kỳ vọng:
- Trả về danh sách notifications của user.

---

### 14) Mark notification as read (REST)

Chọn một notification id trong danh sách ở bước 13, set vào env `NOTIFICATION_ID`.

**Request**
- **Method**: `PATCH`
- **URL**: `{{BASE_URL}}/api/v2/notification-service/notifications/{{NOTIFICATION_ID}}/users/{{USER_ID}}/read`
- **Headers**: `Authorization: Bearer {{ACCESS_TOKEN}}`

Kỳ vọng:
- Notification `is_read=true`.

---

### 15) Delete notification (REST)

**Request**
- **Method**: `DELETE`
- **URL**: `{{BASE_URL}}/api/v2/notification-service/notifications/{{NOTIFICATION_ID}}/users/{{USER_ID}}`
- **Headers**: `Authorization: Bearer {{ACCESS_TOKEN}}`

Kỳ vọng:
- Notification bị xóa khỏi DB và không còn xuất hiện trong bước 13.

---

### 16) Health check notification-service (public)

**Request**
- **Method**: `GET`
- **URL**: `{{BASE_URL}}/api/v2/notification-service/health`

Kỳ vọng:
- 200 OK.

---

### 17) Negative test: không được lấy notifications của user khác

**Request**
- **Method**: `GET`
- **URL**: `{{BASE_URL}}/api/v2/notification-service/notifications/users/{{NEW_USER_ID}}`
- **Headers**: `Authorization: Bearer {{ACCESS_TOKEN}}`

Kỳ vọng:
- 401/403 (vì token hiện tại là của `{{USER_ID}}`, không phải `{{NEW_USER_ID}}`).


---

### 18) Logout

**Request**
- **Method**: `POST`
- **URL**: `{{BASE_URL}}/api/v1/user-service/auth/logout`
- **Headers**: `Authorization: Bearer {{ACCESS_TOKEN}}`

Kỳ vọng:
- 200 OK, message `"Logout successful."`
- Cookie `refresh_token` sẽ bị xóa (Postman: tab Cookies kiểm tra path `/api/v1/user-service/auth/refresh-token`)

