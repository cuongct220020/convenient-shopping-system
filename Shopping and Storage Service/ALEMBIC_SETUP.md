# Hướng dẫn thiết lập Alembic cho Shopping & Storage Service

## Giả định
- Đã cài đặt thư viện `alembic` (thông qua pip hoặc requirements.txt)
- Đã có cấu hình database trong `src/core/database.py`

## Các bước thực hiện

### Bước 1: Khởi tạo Alembic
Chạy lệnh sau trong thư mục gốc của service (`Shopping & Storage Service`):

```bash
alembic init alembic
```

Lệnh này sẽ tạo:
- Thư mục `alembic/` chứa các file cấu hình và migration scripts
- File `alembic.ini` ở thư mục gốc

### Bước 2: Cấu hình `alembic.ini`
Mở file `alembic.ini` và cập nhật phần `sqlalchemy.url`:

```ini
# Tìm dòng này (khoảng dòng 87):
sqlalchemy.url = driver://user:pass@localhost/dbname

# Thay thế bằng database URL của service:
sqlalchemy.url = postgresql+psycopg2://thanh:software20251@software20251db.c3e0884ou51k.ap-southeast-2.rds.amazonaws.com:5432/shopping_pantry_db
```

**Lưu ý:** Nên sử dụng biến môi trường thay vì hardcode. Xem Bước 3 để cấu hình động.

### Bước 3: Cấu hình `alembic/env.py`
Mở file `alembic/env.py` và cập nhật như sau:

```python
from logging.config import fileConfig
import sys
import os

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Thêm đường dẫn src vào sys.path để import models
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

# Import Base từ database config
from core.database import Base

# Import tất cả models để Alembic có thể detect chúng
from models.shopping_plan import ShoppingPlan, Report
from models.storage import Storage, StorableUnit

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target_metadata để Alembic biết cấu trúc database
target_metadata = Base.metadata

# (Tùy chọn) Đọc database URL từ biến môi trường
# import os
# from dotenv import load_dotenv
# load_dotenv()
# database_url = os.getenv("DATABASE_URL")
# config.set_main_option("sqlalchemy.url", database_url)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### Bước 4: Tạo migration đầu tiên (Initial Migration)
Sau khi cấu hình xong, tạo migration script đầu tiên:

```bash
alembic revision --autogenerate -m "Initial database schema"
```

Lệnh này sẽ:
- So sánh models hiện tại với database
- Tạo file migration trong `alembic/versions/` với tên dạng `xxxxx_initial_database_schema.py`

### Bước 5: Kiểm tra migration script
Mở file migration vừa tạo trong `alembic/versions/` và kiểm tra:
- Các bảng được tạo đúng chưa
- Các cột, foreign keys, constraints có đầy đủ không
- Có cần chỉnh sửa gì không

**Lưu ý quan trọng:**
- Nếu database đã có dữ liệu, cần cẩn thận với các thay đổi có thể mất dữ liệu
- Nếu database đã có bảng, có thể cần đánh dấu chúng là "đã tồn tại" trong migration

### Bước 6: Chạy migration
Áp dụng migration vào database:

```bash
alembic upgrade head
```

Lệnh này sẽ:
- Áp dụng tất cả các migration chưa được chạy
- Tạo các bảng và cấu trúc trong database

### Bước 7: (Tùy chọn) Kiểm tra trạng thái
Xem trạng thái migration hiện tại:

```bash
alembic current
```

Xem lịch sử migration:

```bash
alembic history
```

## Các lệnh Alembic thường dùng

### Tạo migration mới
```bash
# Tự động generate từ thay đổi models
alembic revision --autogenerate -m "Mô tả thay đổi"

# Tạo migration trống (tự viết code)
alembic revision -m "Mô tả thay đổi"
```

### Áp dụng migration
```bash
# Áp dụng tất cả migration chưa chạy
alembic upgrade head

# Áp dụng migration cụ thể
alembic upgrade <revision_id>

# Áp dụng migration tiếp theo
alembic upgrade +1
```

### Rollback migration
```bash
# Rollback 1 bước
alembic downgrade -1

# Rollback về revision cụ thể
alembic downgrade <revision_id>

# Rollback tất cả
alembic downgrade base
```

### Xem thông tin
```bash
# Xem revision hiện tại
alembic current

# Xem lịch sử
alembic history

# Xem chi tiết một revision
alembic history <revision_id> --verbose
```

## Lưu ý quan trọng

1. **Luôn kiểm tra migration script trước khi chạy** - Đặc biệt khi sử dụng `--autogenerate`

2. **Backup database trước khi chạy migration** - Đặc biệt trong môi trường production

3. **Không chỉnh sửa migration đã chạy** - Nếu cần thay đổi, tạo migration mới

4. **Sử dụng biến môi trường cho database URL** - Tránh hardcode thông tin nhạy cảm

5. **Import đầy đủ models** - Đảm bảo tất cả models được import trong `env.py` để Alembic có thể detect

6. **Kiểm tra constraints và relationships** - Alembic có thể không detect một số constraints phức tạp, cần kiểm tra thủ công

## Cấu trúc thư mục sau khi thiết lập

```
Shopping & Storage Service/
├── alembic.ini
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── xxxxx_initial_database_schema.py
├── src/
│   ├── models/
│   │   ├── shopping_plan.py
│   │   └── storage.py
│   └── core/
│       └── database.py
└── ...
```

## Troubleshooting

### Lỗi: "Target metadata is not set"
- Kiểm tra `target_metadata = Base.metadata` trong `env.py`
- Đảm bảo Base được import đúng

### Lỗi: "No module named 'models'"
- Kiểm tra `sys.path.insert()` trong `env.py`
- Đảm bảo đường dẫn đến thư mục `src` đúng

### Lỗi: "Table already exists"
- Database đã có bảng, cần đánh dấu trong migration hoặc xóa bảng cũ (cẩn thận với dữ liệu)

### Migration không detect thay đổi
- Đảm bảo models được import trong `env.py`
- Kiểm tra `target_metadata` đã được set đúng
- Thử tạo migration trống và viết thủ công

