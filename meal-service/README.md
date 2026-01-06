# Meal Service

Meal Service là một microservice được xây dựng bằng FastAPI, cung cấp API để quản lý meals (bữa ăn) theo ngày và nhóm người dùng.

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
- Kafka broker (cho messaging, optional)
- Shared package (`../shared`) đã được cài đặt (nếu cần)

## 📦 Cài đặt

### 1. Cài đặt dependencies

```bash
# Từ thư mục meal-service
pip install -r requirements.txt
```

**Lưu ý:** Đảm bảo thư mục `shared` nằm ở cùng cấp với `meal-service` nếu service cần sử dụng shared package.

### 2. Cài đặt database migrations

Service sử dụng Alembic để quản lý database migrations. Để chạy migrations:

```bash
# Từ thư mục meal-service
alembic upgrade head
```

## ⚙️ Cấu hình môi trường

Tạo file `.env` ở thư mục gốc của project (cùng cấp với `meal-service/`) với các biến sau:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_USER=your_db_user
DB_PASSWORD=your_db_password
```

**Lưu ý:** 
- File `.env` phải nằm ở thư mục gốc của project (4 cấp trên `src/core/config.py`)
- Database name mặc định là `meal_db` (được hardcode trong config)

## 🚀 Chạy service trên localhost

Có 2 cách để chạy service:

### Cách 1: Sử dụng uvicorn (Khuyến nghị)

```bash
# Từ thư mục meal-service
uvicorn main:app --host 0.0.0.0 --port 9003 --reload
```

**Tham số:**
- `--host 0.0.0.0`: Lắng nghe trên tất cả interfaces
- `--port 9003`: Port mặc định của service
- `--reload`: Tự động reload khi code thay đổi (chỉ dùng cho development)

### Cách 2: Chạy trực tiếp với Python

```bash
# Từ thư mục meal-service
python main.py
```

**Lưu ý:** `python main.py` sẽ chạy theo port được cấu hình trong code (hiện tại là `8000`).
Nếu muốn chạy đúng port hệ thống (`9003`), hãy dùng uvicorn với `--port 9003`.

## 📚 Xem API Documentation

FastAPI tự động tạo interactive API documentation. Sau khi service đã chạy, mở trình duyệt và truy cập:

```
http://localhost:9003/docs
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
docker build -t meal-service -f meal-service/Dockerfile .
```

### Chạy container

```bash
docker run -d \
  --name meal-service \
  -p 9003:8000 \
  --env-file .env \
  --network shopping-network \
  meal-service
```

**Lưu ý:**
- Đảm bảo file `.env` có đầy đủ các biến môi trường
- Container cần kết nối đến PostgreSQL (có thể qua Docker network)
- Port `9003` sẽ được expose ra host (container listen `8000`)

### Xem logs

```bash
docker logs -f meal-service
```

## 📍 API Endpoints

Service cung cấp các endpoints chính:

### Meals API (`/v1/meals`)
- `GET /v1/meals/` - Lấy danh sách meals theo ngày, group_id và tùy chọn meal_type
- `POST /v1/meals/command` - Xử lý các lệnh tạo/cập nhật/xóa meals (daily meal commands)
- `POST /v1/meals/{id}/cancel` - Hủy một meal
- `POST /v1/meals/{id}/reopen` - Mở lại một meal đã hủy
- `POST /v1/meals/{id}/finish` - Đánh dấu meal đã hoàn thành

## 🛠️ Troubleshooting

### Lỗi kết nối database

- Kiểm tra PostgreSQL đã chạy chưa
- Kiểm tra thông tin kết nối trong `.env`
- Đảm bảo database `meal_db` đã được tạo
- Chạy migrations: `alembic upgrade head`

### Lỗi import shared package

- Đảm bảo thư mục `shared` nằm ở cùng cấp với `meal-service`
- Cài đặt shared package: `pip install -e ../shared[fastapi]`
- Kiểm tra `PYTHONPATH` nếu cần

### Port 9003 đã được sử dụng

- Dùng port khác với uvicorn:
  ```bash
  uvicorn main:app --port 9006 --reload
  ```

## 📝 Notes

- Service sử dụng CORS middleware cho phép tất cả origins (chỉ dùng cho development)
- Database migrations được quản lý bằng Alembic
- Port hệ thống khuyến nghị cho Meal Service: `9003`
- Service có tích hợp scheduler để chạy các scheduled tasks (ví dụ: expire meals)

## 🔗 Liên kết hữu ích

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
