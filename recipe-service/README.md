# Recipe Service

Recipe Service là một microservice được xây dựng bằng FastAPI, cung cấp API để quản lý recipes (công thức nấu ăn) và ingredients (nguyên liệu).

## 📋 Mục lục

- [Yêu cầu hệ thống](#yêu-cầu-hệ-thống)
- [Cài đặt](#cài-đặt)
- [Cấu hình môi trường](#cấu-hình-môi-trường)
- [Chạy service trên localhost](#chạy-service-trên-localhost)
- [Xem API Documentation](#xem-api-documentation)
- [Chạy bằng Docker](#chạy-bằng-docker)

## 🔧 Yêu cầu hệ thống

- Python 3.13+
- PostgreSQL database
- Kafka broker (cho messaging)
- Shared package (`../shared`) đã được cài đặt

## 📦 Cài đặt

### 1. Cài đặt dependencies

```bash
# Từ thư mục recipe-service
pip install -r requirements.txt
```

Lưu ý: `requirements.txt` bao gồm shared package với extra `fastapi`:
```
-e ../shared[fastapi]
```

Đảm bảo thư mục `shared` nằm ở cùng cấp với `recipe-service`.

### 2. Cài đặt database migrations

Service sử dụng Alembic để quản lý database migrations. Để chạy migrations:

```bash
# Từ thư mục recipe-service
alembic upgrade head
```

## ⚙️ Cấu hình môi trường

Tạo file `.env` ở thư mục gốc của project (cùng cấp với `recipe-service/`) với các biến sau:

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
- File `.env` phải nằm ở thư mục gốc của project (4 cấp trên `src/core/config.py`)
- Database name mặc định là `recipe_db` (được hardcode trong config)

## 🚀 Chạy service trên localhost

Có 2 cách để chạy service:

### Cách 1: Sử dụng uvicorn (Khuyến nghị)

```bash
# Từ thư mục recipe-service
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

**Tham số:**
- `--host 0.0.0.0`: Lắng nghe trên tất cả interfaces
- `--port 8001`: Port mặc định của service
- `--reload`: Tự động reload khi code thay đổi (chỉ dùng cho development)

### Cách 2: Chạy trực tiếp với Python

```bash
# Từ thư mục recipe-service
python main.py
```

Service sẽ chạy trên `http://0.0.0.0:8001` (có thể truy cập từ `http://localhost:8001`).

## 📚 Xem API Documentation

FastAPI tự động tạo interactive API documentation. Sau khi service đã chạy, mở trình duyệt và truy cập:

```
http://localhost:8001/docs
```

Swagger UI cung cấp:
- Danh sách tất cả endpoints
- Schema của request/response
- Khả năng test API trực tiếp từ browser
- Try it out: Gửi request và xem response ngay lập tức

## 🐳 Chạy bằng Docker

### Build Docker image

```bash
# Từ thư mục gốc của project
docker build -t recipe-service -f recipe-service/Dockerfile .
```

### Chạy container

```bash
docker run -d \
  --name recipe-service \
  -p 8001:8001 \
  --env-file .env \
  --network shopping-network \
  recipe-service
```

**Lưu ý:**
- Đảm bảo file `.env` có đầy đủ các biến môi trường
- Container cần kết nối đến PostgreSQL và Kafka (có thể qua Docker network)
- Port 8001 sẽ được expose ra host

### Xem logs

```bash
docker logs -f recipe-service
```

## 📍 API Endpoints

Service cung cấp các endpoints chính:

### Ingredients API (`/v2/ingredients`)
- `GET /v2/ingredients/` - Lấy danh sách ingredients (với pagination)
- `GET /v2/ingredients/{id}` - Lấy ingredient theo ID
- `POST /v2/ingredients/` - Tạo ingredient mới
- `PUT /v2/ingredients/{id}` - Cập nhật ingredient
- `DELETE /v2/ingredients/{id}` - Xóa ingredient
- `GET /v2/ingredients/search` - Tìm kiếm ingredients (với cursor pagination)
- `GET /v2/ingredients/filter` - Lọc ingredients theo category (với cursor pagination)

### Recipes API (`/v2/recipes`)
- `GET /v2/recipes/` - Lấy danh sách recipes (với pagination)
- `GET /v2/recipes/{id}` - Lấy recipe theo ID
- `POST /v2/recipes/` - Tạo recipe mới
- `PUT /v2/recipes/{id}` - Cập nhật recipe
- `DELETE /v2/recipes/{id}` - Xóa recipe
- `GET /v2/recipes/search` - Tìm kiếm recipes (với cursor pagination)
- `GET /v2/recipes/recommend` - Lấy recipes được recommend cho group
- `GET /v2/recipes/detailed/{id}` - Lấy recipe chi tiết với components
- `POST /v2/recipes/flattened` - Aggregate ingredients từ nhiều recipes

## 🔍 Pagination

Service sử dụng **cursor-based pagination** cho các endpoints list và search:

```json
{
  "data": [...],
  "next_cursor": 123,
  "size": 100
}
```

**Cách sử dụng:**
1. Request đầu tiên: Không cần `cursor` parameter
2. Request tiếp theo: Sử dụng `next_cursor` từ response trước làm `cursor` parameter
3. Nếu `next_cursor` là `null`, nghĩa là đã hết dữ liệu

**Ví dụ:**
```bash
# Trang đầu tiên
GET /v2/ingredients/?limit=5

# Trang tiếp theo (sử dụng next_cursor từ response trước)
GET /v2/ingredients/?cursor=123&limit=5
```

## 🛠️ Troubleshooting

### Lỗi kết nối database

- Kiểm tra PostgreSQL đã chạy chưa
- Kiểm tra thông tin kết nối trong `.env`
- Đảm bảo database `recipe_db` đã được tạo
- Chạy migrations: `alembic upgrade head`

### Lỗi kết nối Kafka

- Kiểm tra Kafka broker đã chạy chưa
- Kiểm tra `KAFKA_BOOTSTRAP_SERVERS` trong `.env`
- Service vẫn có thể chạy nếu Kafka không có, nhưng messaging features sẽ không hoạt động

### Lỗi import shared package

- Đảm bảo thư mục `shared` nằm ở cùng cấp với `recipe-service`
- Cài đặt shared package: `pip install -e ../shared[fastapi]`
- Kiểm tra `PYTHONPATH` nếu cần

### Port 8001 đã được sử dụng

- Thay đổi port trong `main.py` hoặc dùng `--port` với uvicorn:
  ```bash
  uvicorn main:app --port 8002 --reload
  ```

## 📝 Notes

- Service sử dụng CORS middleware cho phép tất cả origins (chỉ dùng cho development)
- Service tự động tạo Kafka consumers khi khởi động
- Database migrations được quản lý bằng Alembic
- Service chạy trên port 8001 mặc định

## 🔗 Liên kết hữu ích

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

