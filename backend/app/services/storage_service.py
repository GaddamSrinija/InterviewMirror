import asyncio
import functools
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import structlog
from app.config import settings

log = structlog.get_logger()

_executor = ThreadPoolExecutor(max_workers=4)


def _get_storage_root() -> Path:
    """Resolve the storage root directory, creating it if needed."""
    root = Path(settings.STORAGE_DIR)
    if not root.is_absolute():
        # Resolve relative to the backend directory (where the app runs)
        root = Path.cwd() / root
    root.mkdir(parents=True, exist_ok=True)
    return root


def _write_file_sync(data: bytes, object_key: str) -> None:
    """Write bytes to a file under the storage root."""
    dest = _get_storage_root() / object_key
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    log.info("storage_write_success", key=object_key, size=len(data))


def _upload_pdf_sync(pdf_bytes: bytes, object_key: str) -> str:
    """Write a PDF to local storage, return the storage backend identifier."""
    _write_file_sync(pdf_bytes, object_key)
    return "local"


def _upload_snapshot_sync(data: bytes, object_key: str) -> str | None:
    """Write a JSON snapshot to local storage. Returns 'local' on success, None on failure."""
    try:
        _write_file_sync(data, object_key)
        return "local"
    except OSError as e:
        log.warning("storage_snapshot_write_skipped", error=str(e))
        return None


async def upload_pdf(pdf_bytes: bytes, object_key: str) -> str:
    """Async wrapper: write PDF to local filesystem."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        _executor, functools.partial(_upload_pdf_sync, pdf_bytes, object_key)
    )


async def upload_snapshot(data: bytes, object_key: str) -> str | None:
    """Async wrapper: write snapshot JSON to local filesystem."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        _executor, functools.partial(_upload_snapshot_sync, data, object_key)
    )


def get_file_path(object_key: str) -> Path:
    """Resolve an object key to an absolute path. Raises ValueError if not found."""
    path = _get_storage_root() / object_key
    if not path.exists():
        raise ValueError("Report file not found in local storage")
    return path


def delete_file(object_key: str) -> None:
    """Delete a file from local storage. Silently ignores missing files."""
    path = _get_storage_root() / object_key
    path.unlink(missing_ok=True)
    log.info("storage_delete", key=object_key)
