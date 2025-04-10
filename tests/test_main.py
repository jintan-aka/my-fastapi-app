import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from api.db import get_db, Base
from api.main import app
import starlette.status


ASYNC_DB_URL = "sqlite+aiosqlite:///:memory:"  # ✅ オンメモリSQLiteを使用


@pytest_asyncio.fixture
async def async_client():
    # 非同期用のSQLiteエンジンとセッションを作成
    async_engine = create_async_engine(ASYNC_DB_URL, echo=True)
    async_session = sessionmaker(
        bind=async_engine, class_=AsyncSession, autoflush=False, autocommit=False
    )

    # テーブル初期化
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # DIオーバーライドでDBをテスト用に差し替え
    async def override_get_db():
        async with async_session() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    # テスト用クライアント（ASGITransportを使用）
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_create_and_read(async_client):
    # タスク作成
    response = await async_client.post("/tasks", json={"title": "テストタスク"})
    assert response.status_code == starlette.status.HTTP_200_OK
    response_obj = response.json()
    assert response_obj["title"] == "テストタスク"

    # タスクリスト取得
    response = await async_client.get("/tasks")
    assert response.status_code == starlette.status.HTTP_200_OK
    response_obj = response.json()
    assert len(response_obj) == 1
    assert response_obj[0]["title"] == "テストタスク"
    assert response_obj[0]["done"] is False


@pytest.mark.asyncio
async def test_done_flag(async_client):
    # タスク作成
    response = await async_client.post("/tasks", json={"title": "テストタスク2"})
    assert response.status_code == starlette.status.HTTP_200_OK

    # 完了フラグをON
    response = await async_client.put("/tasks/1/done")
    assert response.status_code == starlette.status.HTTP_200_OK

    # 2回目の完了フラグONは400
    response = await async_client.put("/tasks/1/done")
    assert response.status_code == starlette.status.HTTP_400_BAD_REQUEST

    # 完了フラグをOFF
    response = await async_client.delete("/tasks/1/done")
    assert response.status_code == starlette.status.HTTP_200_OK

    # 2回目の完了フラグOFFは404
    response = await async_client.delete("/tasks/1/done")
    assert response.status_code == starlette.status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_calc_pow(async_client):
    response = await async_client.post("/calc_pow", json={"input": 3})
    assert response.status_code == 200
    result = response.json()
    assert result["ans"] == 9


from datetime import date


@pytest.mark.asyncio
async def test_create_task_with_deadline(async_client):
    response = await async_client.post("/tasks", json={
       "title": "締切付きタスク",
       "due_date": "2025-04-15"
    })
    assert response.status_code == starlette.status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "締切付きタスク"
    assert data["due_date"].startswith("2025-04-15")



@pytest.mark.asyncio
async def test_update_task_deadline(async_client):
    # タスクを先に作成
    create = await async_client.post("/tasks", json={
        "title": "締切を更新するタスク",
        "due_date": "2025-04-10"
    })
    task_id = create.json()["id"]

    # 締切を更新
    update = await async_client.put(f"/tasks/{task_id}", json={
        "title": "締切を更新するタスク",
        "due_date": "2025-04-20"
    })
    assert update.status_code == starlette.status.HTTP_200_OK
    assert update.json()["due_date"].startswith("2025-04-20")

