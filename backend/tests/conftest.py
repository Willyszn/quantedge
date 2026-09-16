from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base
from app.market_data.mock_provider import MockMarketDataProvider
from app.sentiment.mock_provider import MockSentimentProvider

TEST_DATABASE_URL = "postgresql+asyncpg://quantedge:quantedge@localhost:5432/quantedge_test"


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    import app.models  # noqa: F401 - register all tables on Base.metadata

    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest_asyncio.fixture(autouse=True)
async def _flush_redis():
    import app.core.redis_client as redis_client_module

    # The Redis client is a module-level singleton bound to whichever event
    # loop created it. pytest-asyncio gives each test function its own
    # loop, so reusing a client created in a prior (now-closed) loop raises
    # "Event loop is closed". Resetting the singleton forces a fresh client
    # bound to the current test's loop.
    redis_client_module._redis_pool = None
    client = redis_client_module.get_redis()
    await client.flushdb()
    yield
    await client.flushdb()


@pytest.fixture
def market_provider() -> MockMarketDataProvider:
    return MockMarketDataProvider()


@pytest.fixture
def sentiment_provider() -> MockSentimentProvider:
    return MockSentimentProvider()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    from app.api.dependencies import get_db_session
    from app.main import app

    async def override_get_db_session():
        yield db_session

    app.dependency_overrides[get_db_session] = override_get_db_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
