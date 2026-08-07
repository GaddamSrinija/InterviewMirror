
  import pytest
  from httpx import AsyncClient
  from unittest.mock import patch, AsyncMock


  @pytest.mark.asyncio
  @patch("app.api.repositories.validate_repository", new_callable=AsyncMock)
  @patch("app.api.repositories.run_analysis")
  async def test_import_repository(mock_analysis, mock_validate, client: AsyncClient, auth_headers, db_session):
      from app.models.user import User
      from app.services.auth_service import hash_password
      user = User(id=1, email="t@t.com", username="tuser", hashed_password=hash_password("p"))
      db_session.add(user)
      await db_session.commit()

      mock_validate.return_value = {
          "description": "Test repo",
          "language": "Python",
          "default_branch": "main",
      }

      response = await client.post(
          "/api/repositories/",
          json={"github_url": "https://github.com/owner/repo"},
          headers=auth_headers,
      )
      assert response.status_code == 201
      data = response.json()
      assert data["owner"] == "owner"
      assert data["name"] == "repo"
