
  import pytest
  from unittest.mock import patch, MagicMock


  @pytest.mark.asyncio
  async def test_download_nonexistent_report(client, auth_headers, db_session):
      from app.models.user import User
      from app.services.auth_service import hash_password
      user = User(id=1, email="t@t.com", username="tuser", hashed_password=hash_password("p"))
      db_session.add(user)
      await db_session.commit()

      response = await client.get("/api/reports/999/download", headers=auth_headers)
      assert response.status_code == 404
