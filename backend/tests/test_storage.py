
  import os
  import pytest
  from pathlib import Path
  from app.services.storage_service import upload_pdf, upload_snapshot, get_file_path, delete_file


  @pytest.fixture
  def storage_dir(tmp_path, monkeypatch):
      """Point STORAGE_DIR to a temporary directory for testing."""
      monkeypatch.setattr("app.services.storage_service.settings", type("S", (), {"STORAGE_DIR": str(tmp_path)})())
      return tmp_path


  @pytest.mark.asyncio
  async def test_upload_pdf(storage_dir):
      pdf_bytes = b"%PDF-1.4 fake pdf content"
      backend = await upload_pdf(pdf_bytes, "reports/test/report.pdf")
      assert backend == "local"

      written = (storage_dir / "reports" / "test" / "report.pdf").read_bytes()
      assert written == pdf_bytes


  @pytest.mark.asyncio
  async def test_upload_snapshot(storage_dir):
      data = b'{"files": {}, "metadata": {}}'
      backend = await upload_snapshot(data, "snapshots/owner/repo/1.json")
      assert backend == "local"

      written = (storage_dir / "snapshots" / "owner" / "repo" / "1.json").read_bytes()
      assert written == data


  @pytest.mark.asyncio
  async def test_get_file_path(storage_dir):
      pdf_bytes = b"%PDF-1.4 content"
      await upload_pdf(pdf_bytes, "reports/test/report.pdf")

      path = get_file_path("reports/test/report.pdf")
      assert path.exists()
      assert path.read_bytes() == pdf_bytes


  @pytest.mark.asyncio
  async def test_get_file_path_missing(storage_dir):
      with pytest.raises(ValueError, match="not found"):
          get_file_path("nonexistent/key.pdf")


  @pytest.mark.asyncio
  async def test_delete_file(storage_dir):
      pdf_bytes = b"%PDF-1.4 content"
      await upload_pdf(pdf_bytes, "reports/test/report.pdf")

      file_path = storage_dir / "reports" / "test" / "report.pdf"
      assert file_path.exists()

      delete_file("reports/test/report.pdf")
      assert not file_path.exists()


  @pytest.mark.asyncio
  async def test_delete_file_missing(storage_dir):
      # Should not raise
      delete_file("nonexistent/key.pdf")


  @pytest.mark.asyncio
  async def test_creates_nested_directories(storage_dir):
      data = b"nested content"
      await upload_pdf(data, "a/b/c/d/e/file.pdf")

      path = storage_dir / "a" / "b" / "c" / "d" / "e" / "file.pdf"
      assert path.exists()
      assert path.read_bytes() == data
