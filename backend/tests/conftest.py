
  import pytest
  import pytest_asyncio
  from httpx import AsyncClient, ASGITransport
  from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

  from app.main import app
  from app.database import get_db
  from app.models import Base
  from app.services.auth_service import create_access_token

  TEST_DB_URL = "sqlite+aiosqlite:///./test.db"


  @pytest_asyncio.fixture
  async def db_session():
      engine = create_async_engine(TEST_DB_URL, echo=False)
      async with engine.begin() as conn:
          await conn.run_sync(Base.metadata.create_all)
      session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
      async with session_factory() as session:
          yield session
      async with engine.begin() as conn:
          await conn.run_sync(Base.metadata.drop_all)
      await engine.dispose()


  @pytest_asyncio.fixture
  async def client(db_session):
      async def override_db():
          yield db_session

      app.dependency_overrides[get_db] = override_db
      transport = ASGITransport(app=app)
      async with AsyncClient(transport=transport, base_url="http://test") as c:
          yield c
      app.dependency_overrides.clear()


  @pytest.fixture
  def auth_headers():
      token = create_access_token(1)
      return {"Authorization": f"Bearer {token}"}
