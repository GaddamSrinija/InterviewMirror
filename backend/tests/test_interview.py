
  import pytest
  from unittest.mock import patch, AsyncMock


  @pytest.mark.asyncio
  async def test_get_nonexistent_session(client, auth_headers, db_session):
      from app.models.user import User
      from app.services.auth_service import hash_password
      user = User(id=1, email="t@t.com", username="tuser", hashed_password=hash_password("p"))
      db_session.add(user)
      await db_session.commit()

      response = await client.get("/api/interviews/999", headers=auth_headers)
      assert response.status_code == 404
