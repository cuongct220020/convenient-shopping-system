import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from shopping_shared.databases.base_model import Base
from app.config import Config

# Lấy connection string từ Config
# Lưu ý: Trong môi trường CI/CD thực tế, nên dùng DB riêng cho test.
DATABASE_URL = Config.POSTGRESQL.DATABASE_URI

@pytest.fixture(scope="session")
async def db_engine():
    """Tạo Async Engine cho toàn bộ session test."""
    engine = create_async_engine(DATABASE_URL, echo=False)
    
    # Tạo bảng (Create Tables)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all) # Xóa sạch trước khi tạo
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Dọn dẹp (Teardown)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture
async def db_session(db_engine):
    """
    Cung cấp DB Session cho từng test case.
    Tự động rollback sau khi test xong để đảm bảo tính cô lập.
    """
    connection = await db_engine.connect()
    transaction = await connection.begin()
    
    session_maker = async_sessionmaker(bind=connection, expire_on_commit=False)
    session = session_maker()
    
    yield session
    
    await session.close()
    await transaction.rollback()
    await connection.close()
