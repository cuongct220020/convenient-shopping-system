# Chiến lược Caching cho User Service

Tài liệu này mô tả chi tiết kế hoạch triển khai Caching nhằm tối ưu hóa hiệu năng cho các endpoint trong User Service, giảm tải cho Database và tăng tốc độ phản hồi.

> **Lưu ý:** Việc triển khai Caching sẽ được thực hiện sau khi hoàn tất kiểm thử các tối ưu hóa về truy vấn Database (Query Optimization).

## 1. Mục tiêu
*   **Giảm tải Database:** Giảm thiểu các truy vấn nặng như `COUNT(*)` và `OFFSET/LIMIT` trong các trang danh sách.
*   **Tăng tốc độ phản hồi:** Giảm latency cho cả Admin Dashboard và các tính năng người dùng.
*   **Đảm bảo tính nhất quán (Consistency):** Dữ liệu hiển thị phải được cập nhật ngay lập tức khi có thay đổi (Create/Update/Delete).

## 2. Kiến trúc Caching

Sử dụng mô hình **Cache-Aside (Lazy Loading)** kết hợp **Write-Through / Cache Invalidation**.

*   **Read (GET):** Kiểm tra Redis -> Nếu có trả về ngay -> Nếu không query DB và lưu vào Redis.
*   **Write (POST/PUT/DELETE):** Thực hiện thay đổi DB -> **Xóa (Invalidate)** cache liên quan ngay lập tức.

## 3. Chi tiết Chiến lược từng Endpoint

### A. Quản lý User Admin (`/admin/users`)

| Endpoint | Hành động | Chiến lược | Key Redis Pattern | TTL (Time-To-Live) |
| :--- | :--- | :--- | :--- | :--- |
| `GET /` | Xem danh sách | **Cache** | `admin:users:list:p{page}:s{size}` | **60 giây** |
| `GET /{id}` | Xem chi tiết | **Cache** | `admin:users:detail:{id}` | **5 phút** |
| `POST /` | Tạo mới | **Invalidate** | Xóa `admin:users:list:*` | N/A |
| `PUT /{id}` | Cập nhật | **Invalidate** | Xóa `admin:users:list:*`<br>Xóa `admin:users:detail:{id}` | N/A |
| `DELETE /{id}` | Xóa | **Invalidate** | Xóa `admin:users:list:*`<br>Xóa `admin:users:detail:{id}` | N/A |

### B. Quản lý Group Admin (`/admin/groups`)

| Endpoint | Hành động | Chiến lược | Key Redis Pattern | TTL |
| :--- | :--- | :--- | :--- | :--- |
| `GET /` | Xem danh sách | **Cache** | `admin:groups:list:p{page}:s{size}` | **60 giây** |
| `GET /{id}` | Xem chi tiết | **Cache** | `admin:groups:detail:{id}` | **5 phút** |
| `GET /{id}/members` | Xem thành viên | **Cache** | `admin:groups:{id}:members` | **60 giây** |
| `POST /` | Tạo mới | **Invalidate** | Xóa `admin:groups:list:*` | N/A |
| `PUT /{id}` | Cập nhật | **Invalidate** | Xóa `admin:groups:list:*`<br>Xóa `admin:groups:detail:{id}` | N/A |
| `DELETE /{id}` | Xóa | **Invalidate** | Xóa `admin:groups:list:*`<br>Xóa `admin:groups:detail:{id}` | N/A |
| `POST .../members` | Thêm thành viên | **Invalidate** | Xóa `admin:groups:{id}:members` | N/A |
| `DELETE .../members`| Xóa thành viên | **Invalidate** | Xóa `admin:groups:{id}:members` | N/A |

### C. Quản lý Nhóm Gia đình (`/groups`)

| Endpoint | Hành động | Chiến lược | Key Redis Pattern | TTL |
| :--- | :--- | :--- | :--- | :--- |
| `GET /` | Xem danh sách nhóm người dùng | **Cache** | `user-service:groups:user:{user_id}:list` | **5 phút** |
| `GET /{group_id}` | Xem chi tiết nhóm | **Cache** | `user-service:groups:detail:{group_id}` | **5 phút** |
| `POST /` | Tạo mới nhóm | **Invalidate** | Xóa `user-service:groups:user:{user_id}:list` | N/A |
| `PUT /{group_id}` | Cập nhật nhóm | **Invalidate** | Xóa `user-service:groups:detail:{group_id}` | N/A |
| `DELETE /{group_id}` | Xóa nhóm | **Invalidate** | Xóa `user-service:groups:detail:{group_id}`<br>Xóa `user-service:groups:user:{user_id}:list` | N/A |

### D. Quản lý Thành viên Nhóm (`/groups/{group_id}/members`)

| Endpoint | Hành động | Chiến lược | Key Redis Pattern | TTL |
| :--- | :--- | :--- | :--- | :--- |
| `GET /` | Xem danh sách thành viên | **Cache** | `user-service:groups:{group_id}:members` | **2 phút** |
| `POST /` | Thêm thành viên | **Invalidate** | Xóa `user-service:groups:{group_id}:members` | N/A |
| `DELETE /{user_id}` | Xóa thành viên | **Invalidate** | Xóa `user-service:groups:{group_id}:members`<br>Xóa `user-service:groups:user:{user_id}:list` | N/A |
| `PATCH /{user_id}` | Cập nhật vai trò | **Invalidate** | Xóa `user-service:groups:{group_id}:members` | N/A |

### E. Quản lý Hồ sơ Thành viên (`/groups/{group_id}/members/{user_id}/identity`, `/groups/{group_id}/members/{user_id}/health`)

| Endpoint | Hành động | Chiến lược | Key Redis Pattern | TTL |
| :--- | :--- | :--- | :--- | :--- |
| `GET /identity` | Xem hồ sơ định danh | **Cache** | `user-service:profiles:identity:{user_id}` | **15 phút** |
| `GET /health` | Xem hồ sơ sức khỏe | **Cache** | `user-service:profiles:health:{user_id}` | **15 phút** |
| `PUT /identity` | Cập nhật hồ sơ định danh | **Invalidate** | Xóa `user-service:profiles:identity:{user_id}` | N/A |
| `PUT /health` | Cập nhật hồ sơ sức khỏe | **Invalidate** | Xóa `user-service:profiles:health:{user_id}` | N/A |

### F. Kiểm tra Quyền Truy cập Nhóm (`/groups/{group_id}/access-check`)

| Endpoint | Hành động | Chiến lược | Key Redis Pattern | TTL |
| :--- | :--- | :--- | :--- | :--- |
| `POST /` | Kiểm tra quyền truy cập | **Cache** | `user-service:access:{group_id}:{user_id}` | **1 phút** |

### G. Quản lý Hồ sơ Người dùng (`/users/me`)

| Endpoint | Hành động | Chiến lược | Key Redis Pattern | TTL |
| :--- | :--- | :--- | :--- | :--- |
| `GET /` | Xem thông tin người dùng | **Cache** | `user-service:users:me:{user_id}:core` | **10-15 phút** |
| `PATCH /` | Cập nhật thông tin người dùng | **Invalidate** | Xóa `user-service:users:me:{user_id}:core` | N/A |

### H. Quản lý Hồ sơ Định danh (`/users/me/profile/identity`)

| Endpoint | Hành động | Chiến lược | Key Redis Pattern | TTL |
| :--- | :--- | :--- | :--- | :--- |
| `GET /` | Xem hồ sơ định danh | **Cache** | `user-service:profiles:me:{user_id}:identity` | **30 phút - 1 giờ** |
| `PATCH /` | Cập nhật hồ sơ định danh | **Invalidate** | Xóa `user-service:profiles:me:{user_id}:identity` | N/A |

### I. Quản lý Hồ sơ Sức khỏe (`/users/me/profile/health`)

| Endpoint | Hành động | Chiến lược | Key Redis Pattern | TTL |
| :--- | :--- | :--- | :--- | :--- |
| `GET /` | Xem hồ sơ sức khỏe | **Cache** | `user-service:profiles:me:{user_id}:health` | **15-30 phút** |
| `PATCH /` | Cập nhật hồ sơ sức khỏe | **Invalidate** | Xóa `user-service:profiles:me:{user_id}:health` | N/A |

### J. Quản lý Thẻ Người dùng (`/users/me/tags`)

| Endpoint | Hành động | Chiến lược | Key Redis Pattern | TTL |
| :--- | :--- | :--- | :--- | :--- |
| `GET /` | Xem tất cả thẻ người dùng | **Cache** | `user-service:tags:me:{user_id}:all` | **5-10 phút** |
| `POST /` | Thêm thẻ người dùng | **Invalidate** | Xóa `user-service:tags:me:{user_id}:all` | N/A |
| `PUT /category/{category}` | Cập nhật thẻ theo danh mục | **Invalidate** | Xóa `user-service:tags:me:{user_id}:all` | N/A |
| `POST /delete` | Xóa thẻ người dùng | **Invalidate** | Xóa `user-service:tags:me:{user_id}:all` | N/A |

## 4. Kế hoạch Thực hiện (Coding)

### Bước 1: Nâng cấp `RedisService`
Cập nhật `user-service/app/services/redis_service.py` để thêm các hàm helper:
- `get_cache(key: str) -> dict | None`
- `set_cache(key: str, data: dict, ttl: int)`
- `delete_pattern(pattern: str)` (Sử dụng SCAN để xóa hàng loạt key danh sách).

### Bước 2: Tạo Decorator `@cache_response`
Tạo decorator để tự động hóa việc cache cho các View GET, giúp code gọn gàng hơn.
```python
@cache_response(key_pattern="admin:users:list:p{page}:s{page_size}", ttl=60)
async def get(self, request):
    ...
```

### Bước 3: Tích hợp Invalidation vào Service
Sửa các hàm `create`, `update`, `delete` trong `AdminUserService`, `AdminGroupService` và `FamilyGroupService` để gọi `RedisService.delete_pattern(...)` sau khi thao tác DB thành công.

### Bước 4: Tích hợp Caching vào View
Áp dụng decorator hoặc gọi trực tiếp `RedisService` trong các hàm `GET` của `AdminUsersView`, `AdminGroupsView`, và các view quản lý nhóm gia đình.

## 5. Rủi ro & Giải pháp

1.  **Stale Data (Dữ liệu cũ):**
    *   *Rủi ro:* Người dùng vừa tạo nhóm xong quay lại trang danh sách vẫn chưa thấy.
    *   *Giải pháp:* Cơ chế Invalidation (Xóa cache) đảm bảo cache danh sách bị xóa ngay lập tức khi có ghi.
2.  **Race Condition:**
    *   *Rủi ro:* Hai người dùng cùng cập nhật.
    *   *Giải pháp:* TTL ngắn (1-5 phút) giảm thiểu thời gian hiển thị sai lệch.
3.  **Redis Memory:**
    *   *Rủi ro:* Lưu quá nhiều trang cache.
    *   *Giải pháp:* TTL ngắn tự động dọn dẹp. Key pattern cụ thể giúp dễ dàng quản lý.
