
  import pytest
  from httpx import AsyncClient


  @pytest.mark.asyncio
  async def test_register(client: AsyncClient):
      response = await client.post("/api/auth/register", json={
          "email": "test@example.com",
          "username": "testuser",
          "password": "securepass123",
      })
      assert response.status_code == 200
      data = response.json()
      assert "access_token" in data
      assert data["user"]["email"] == "test@example.com"


  @pytest.mark.asyncio
  async def test_register_duplicate(client: AsyncClient):
      await client.post("/api/auth/register", json={
          "email": "dup@example.com",
          "username": "dupuser",
          "password": "pass123",
      })
      response = await client.post("/api/auth/register", json={
          "email": "dup@example.com",
          "username": "dupuser2",
          "password": "pass123",
      })
      assert response.status_code == 409


  @pytest.mark.asyncio
  async def test_login(client: AsyncClient):
      await client.post("/api/auth/register", json={
          "email": "login@example.com",
          "username": "loginuser",
          "password": "pass123",
      })
      response = await client.post("/api/auth/login", json={
          "email": "login@example.com",
          "password": "pass123",
      })
      assert response.status_code == 200
      assert "access_token" in response.json()


  @pytest.mark.asyncio
  async def test_login_invalid(client: AsyncClient):
      response = await client.post("/api/auth/login", json={
          "email": "nobody@example.com",
          "password": "wrong",
      })
      assert response.status_code == 401
