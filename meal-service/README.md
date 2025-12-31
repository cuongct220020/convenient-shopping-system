# Meal Service

Service quản lý các bữa ăn (meals) cho hệ thống. Service này cung cấp API để tạo, cập nhật, xóa và quản lý các bữa ăn theo ngày và nhóm người dùng.

## Yêu cầu

- Python 3.11+
- PostgreSQL database
- Kafka (nếu sử dụng messaging features)

## Cài đặt

1. **Tạo virtual environment:**

```bash
python -m venv venv
```

2. **Kích hoạt virtual environment:**

   - Trên Windows:
   ```bash
   venv\Scripts\activate
   ```

   - Trên Linux/Mac:
   ```bash
   source venv/bin/activate
   ```

3. **Cài đặt dependencies:**

```bash
pip install -r requirements.txt
```

4. **Cài đặt shared package:**

```bash
cd ../shared
pip install -e .
cd ../meal-service
```

## Cấu hình

Tạo file `.env` ở thư mục gốc của project (cùng cấp với `meal-service`, `recipe-service`, v.v.) với nội dung sau:

```env
DB_HOST=localhost
DB_PORT=5432
DB_USER=your_db_user
DB_PASSWORD=your_db_password
```

**Lưu ý:** File `.env` phải được đặt ở thư mục gốc của workspace (cùng cấp với các thư mục `meal-service`, `recipe-service`, `shared`, v.v.), không phải trong thư mục `meal-service`.

## Database Migration

1. **Tạo database:**

Tạo database PostgreSQL với tên `meal_db`:

```sql
CREATE DATABASE meal_db;
```

2. **Chạy migrations:**

```bash
alembic upgrade head
```

3. **Tạo migration mới (nếu cần):**

```bash
alembic revision --autogenerate -m "migration message"
alembic upgrade head
```

## Chạy Local

1. **Khởi động service:**

```bash
python main.py
```

Hoặc sử dụng uvicorn trực tiếp:

```bash
uvicorn main:app --host 0.0.0.0 --port 8003 --reload
```

2. **Service sẽ chạy tại:**

```
http://localhost:8003
```

## API Documentation

Sau khi khởi động service, bạn có thể truy cập tài liệu API tại:

```
http://localhost:8003/docs
```

## API Endpoints

### Base URL
```
http://localhost:8003/v1/meals
```

### Các endpoints chính:

- `GET /` - Lấy danh sách meals theo ngày và group_id
- `POST /command` - Xử lý các lệnh tạo/cập nhật/xóa meals
- `POST /{id}/cancel` - Hủy một meal
- `POST /{id}/reopen` - Mở lại một meal đã hủy
- `POST /{id}/finish` - Đánh dấu meal đã hoàn thành

Chi tiết về các endpoint và test cases, xem file `meal_test_cases.md`.

## Development

### Chạy với reload (auto-reload khi code thay đổi):

```bash
uvicorn main:app --host 0.0.0.0 --port 8003 --reload
```

### Debug mode:

Service mặc định chạy với log level `debug`. Để thay đổi, sửa trong `main.py`:

```python
uvicorn.run("main:app", host="0.0.0.0", port=8003, reload=False, log_level="info")
```

## Notes

- Service sử dụng PostgreSQL database với tên database là `meal_db`
- Service sử dụng Alembic để quản lý database migrations
- Service có tích hợp scheduler để chạy các scheduled tasks (ví dụ: expire meals)
- Service chạy trên port 8003 mặc định

