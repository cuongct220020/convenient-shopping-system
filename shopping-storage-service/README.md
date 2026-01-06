# Shopping & Storage Service

Shopping & Storage Service là một microservice được xây dựng bằng FastAPI, cung cấp API để quản lý shopping plans (kế hoạch mua sắm), storages (kho lưu trữ) và storable units (đơn vị lưu trữ).

## 📋 Mục lục

-   [Yêu cầu hệ thống](#yêu-cầu-hệ-thống)
-   [Cài đặt](#cài-đặt)
-   [Cấu hình môi trường](#cấu-hình-môi-trường)
-   [Chạy service trên localhost](#chạy-service-trên-localhost)
-   [Xem API Documentation](#xem-api-documentation)
-   [Chạy bằng Docker](#chạy-bằng-docker)
-   [Pagination](#pagination)

## 🔧 Yêu cầu hệ thống

-   Python 3.13+
-   PostgreSQL database
-   Kafka broker (cho messaging)
-   Shared package (`../shared`) đã được cài đặt

## 📦 Cài đặt

### 1. Cài đặt dependencies

```bash
# Từ thư mục shopping-storage-service
pip install -r requirements.txt
```

Lưu ý: `requirements.txt` bao gồm shared package với extra `fastapi`:

```
-e ../shared[fastapi]
```

Đảm bảo thư mục `shared` nằm ở cùng cấp với `shopping-storage-service`.

### 2. Cài đặt database migrations

Service sử dụng Alembic để quản lý database migrations. Để chạy migrations:

```bash
# Từ thư mục shopping-storage-service
alembic upgrade head
```

## ⚙️ Cấu hình môi trường

Tạo file `.env` ở thư mục gốc của project (cùng cấp với `shopping-storage-service/`) với các biến sau:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_USER=your_db_user
DB_PASSWORD=your_db_password

# Kafka Configuration (optional, có giá trị mặc định)
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
```

**Lưu ý:**

-   File `.env` phải nằm ở thư mục gốc của project (4 cấp trên `src/core/config.py`)
-   Database name mặc định là `shopping_storage_db` (được hardcode trong config)

## 🚀 Chạy service trên localhost

Có 2 cách để chạy service:

### Cách 1: Sử dụng uvicorn (Khuyến nghị)

```bash
# Từ thư mục shopping-storage-service
uvicorn main:app --host 0.0.0.0 --port 8002 --reload
```

**Tham số:**

-   `--host 0.0.0.0`: Lắng nghe trên tất cả interfaces
-   `--port 8002`: Port mặc định của service
-   `--reload`: Tự động reload khi code thay đổi (chỉ dùng cho development)

### Cách 2: Chạy trực tiếp với Python

```bash
# Từ thư mục shopping-storage-service
python main.py
```

Service sẽ chạy trên `http://0.0.0.0:8002` (có thể truy cập từ `http://localhost:8002`).

## 📚 Xem API Documentation

FastAPI tự động tạo interactive API documentation. Sau khi service đã chạy, mở trình duyệt và truy cập:

```
http://localhost:8002/docs
```

Swagger UI cung cấp:

-   Danh sách tất cả endpoints
-   Schema của request/response
-   Khả năng test API trực tiếp từ browser
-   Try it out: Gửi request và xem response ngay lập tức

## 🐳 Chạy bằng Docker

### Build Docker image

```bash
# Từ thư mục gốc của project
docker build -t shopping-storage-service -f shopping-storage-service/Dockerfile .
```

### Chạy container

```bash
docker run -d \
  --name shopping-storage-service \
  -p 8002:8002 \
  --env-file .env \
  --network shopping-network \
  shopping-storage-service
```

**Lưu ý:**

-   Đảm bảo file `.env` có đầy đủ các biến môi trường
-   Container cần kết nối đến PostgreSQL và Kafka (có thể qua Docker network)
-   Port 8002 sẽ được expose ra host

### Xem logs

```bash
docker logs -f shopping-storage-service
```

## 📍 API Endpoints

Service cung cấp các endpoints chính:

### Shopping Plans API (`/v1/shopping_plans`)

-   `GET /v1/shopping_plans/` - Lấy danh sách shopping plans (với pagination)
-   `GET /v1/shopping_plans/{id}` - Lấy shopping plan theo ID
-   `POST /v1/shopping_plans/` - Tạo shopping plan mới
-   `PUT /v1/shopping_plans/{id}` - Cập nhật shopping plan
-   `DELETE /v1/shopping_plans/{id}` - Xóa shopping plan
-   `GET /v1/shopping_plans/filter` - Lọc shopping plans theo group_id và plan_status (với cursor pagination)
-   `POST /v1/shopping_plans/{id}/assign` - Gán shopping plan cho assignee
-   `POST /v1/shopping_plans/{id}/unassign` - Hủy gán shopping plan
-   `POST /v1/shopping_plans/{id}/cancel` - Hủy shopping plan
-   `POST /v1/shopping_plans/{id}/reopen` - Mở lại shopping plan đã hủy
-   `POST /v1/shopping_plans/{id}/report` - Báo cáo hoàn thành shopping plan

### Storages API (`/v1/storages`)

-   `GET /v1/storages/` - Lấy danh sách storages (với pagination)
-   `GET /v1/storages/{id}` - Lấy storage theo ID
-   `POST /v1/storages/` - Tạo storage mới
-   `PUT /v1/storages/{id}` - Cập nhật storage
-   `DELETE /v1/storages/{id}` - Xóa storage

### Storable Units API (`/v1/storable_units`)

-   `GET /v1/storable_units/` - Lấy danh sách storable units (với pagination)
-   `GET /v1/storable_units/{id}` - Lấy storable unit theo ID
-   `POST /v1/storable_units/` - Tạo storable unit mới
-   `PUT /v1/storable_units/{id}` - Cập nhật storable unit
-   `GET /v1/storable_units/filter` - Lọc storable units theo group_id, storage_id và unit_name (với cursor pagination)
-   `GET /v1/storable_units/stacked` - Lấy danh sách storable units đã được nhóm (stacked) theo storage_id (với cursor pagination)
-   `POST /v1/storable_units/{id}/consume` - Tiêu thụ một lượng từ storable unit

## 🔍 Pagination

Service sử dụng **cursor-based pagination** cho các endpoints list và filter:

### Format Response

Response có dạng:

```json
{
  "data": [...],
  "next_cursor": 123,
  "size": 10,
  "has_more": true
}
```

**Các trường:**

-   `data`: Mảng chứa các items trong trang hiện tại
-   `next_cursor`: Giá trị cursor để lấy trang tiếp theo (số nguyên, ID của item cuối cùng). Nếu `null` nghĩa là đã hết dữ liệu
-   `size`: Số lượng items trong trang hiện tại
-   `has_more`: Boolean cho biết còn dữ liệu để lấy không

### Cách sử dụng

1. **Request đầu tiên:** Không cần `cursor` parameter
2. **Request tiếp theo:** Sử dụng `next_cursor` từ response trước làm `cursor` parameter
3. **Kết thúc:** Nếu `next_cursor` là `null` hoặc `has_more` là `false`, nghĩa là đã hết dữ liệu

### Parameters

-   `cursor` (optional): Giá trị cursor từ response trước (mặc định: null để lấy trang đầu)
-   `limit` (optional): Số lượng items mỗi trang (mặc định: 100, tối thiểu: 1)

### Ví dụ

```bash
# Trang đầu tiên
GET /v1/shopping_plans/?limit=5

# Response:
# {
#   "data": [...],
#   "next_cursor": 123,
#   "size": 5,
#   "has_more": true
# }

# Trang tiếp theo (sử dụng next_cursor từ response trước)
GET /v1/shopping_plans/?cursor=123&limit=5

# Response:
# {
#   "data": [...],
#   "next_cursor": 456,
#   "size": 5,
#   "has_more": true
# }

# Trang cuối
GET /v1/shopping_plans/?cursor=456&limit=5

# Response:
# {
#   "data": [...],
#   "next_cursor": null,
#   "size": 3,
#   "has_more": false
# }
```

## 🛠️ Troubleshooting

### Lỗi kết nối database

-   Kiểm tra PostgreSQL đã chạy chưa
-   Kiểm tra thông tin kết nối trong `.env`
-   Đảm bảo database `shopping_storage_db` đã được tạo
-   Chạy migrations: `alembic upgrade head`

### Lỗi kết nối Kafka

-   Kiểm tra Kafka broker đã chạy chưa
-   Kiểm tra `KAFKA_BOOTSTRAP_SERVERS` trong `.env`
-   Service vẫn có thể chạy nếu Kafka không có, nhưng messaging features sẽ không hoạt động

### Lỗi import shared package

-   Đảm bảo thư mục `shared` nằm ở cùng cấp với `shopping-storage-service`
-   Cài đặt shared package: `pip install -e ../shared[fastapi]`
-   Kiểm tra `PYTHONPATH` nếu cần

### Port 8002 đã được sử dụng

-   Thay đổi port trong `main.py` hoặc dùng `--port` với uvicorn:
    ```bash
    uvicorn main:app --port 8003 --reload
    ```

## 📝 Notes

-   Service sử dụng CORS middleware cho phép tất cả origins (chỉ dùng cho development)
-   Service tự động tạo Kafka consumers khi khởi động
-   Database migrations được quản lý bằng Alembic
-   Service chạy trên port 8002 mặc định
-   Service có tích hợp scheduler để chạy các scheduled tasks

## 🔗 Liên kết hữu ích

-   [FastAPI Documentation](https://fastapi.tiangolo.com/)
-   [Alembic Documentation](https://alembic.sqlalchemy.org/)
-   [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
