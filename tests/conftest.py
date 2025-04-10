import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from api.main import app
from api.db import Base, get_db

# テスト用 SQLite（メモリDB）
DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# 非同期エンジンとセッションの設定
engine_test = create_async_engine(DATABASE_URL, echo=True, poolclass=NullPool)
AsyncSessionLocal = async_sessionmaker(engine_test, expire_on_commit=False)

# DB初期化（テーブル作成 → テスト終了後に削除）
@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# get_db をテスト用DBに差し替える
async def override_get_db():
    async with AsyncSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

# HTTPクライアント fixture（FastAPI + AsyncClient）
@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
