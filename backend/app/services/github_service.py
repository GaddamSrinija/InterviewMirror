import httpx
import structlog
from app.config import settings

log = structlog.get_logger()

GITHUB_API = "https://api.github.com"
IGNORED_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".woff", ".woff2",
    ".ttf", ".eot", ".mp4", ".mp3", ".zip", ".tar", ".gz", ".lock",
    ".min.js", ".min.css", ".map", ".pyc", ".class", ".o", ".so", ".dll",
}
IGNORED_DIRS = {
    "node_modules", ".git", "__pycache__", ".venv", "venv", "dist", "build",
    ".next", ".nuxt", "vendor", ".idea", ".vscode",
}
MAX_FILE_SIZE = 100_000


def _headers() -> dict:
    headers = {"Accept": "application/vnd.github.v3+json"}
    if settings.GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {settings.GITHUB_TOKEN}"
    return headers


def parse_github_url(url: str) -> tuple[str, str]:
    url = url.rstrip("/")
    if url.endswith(".git"):
        url = url[:-4]
    parts = url.split("/")
    owner = parts[-2]
    name = parts[-1]
    return owner, name


async def validate_repository(owner: str, name: str) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{GITHUB_API}/repos/{owner}/{name}", headers=_headers()
        )
        if resp.status_code != 200:
            raise ValueError(f"Repository not found or not accessible: {owner}/{name}")
        return resp.json()


async def get_repo_tree(owner: str, name: str, branch: str) -> list[dict]:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{GITHUB_API}/repos/{owner}/{name}/git/trees/{branch}",
            headers=_headers(),
            params={"recursive": "1"},
        )
        if resp.status_code != 200:
            raise ValueError("Failed to fetch repository tree")
        tree = resp.json().get("tree", [])
        files = []
        for item in tree:
            if item["type"] != "blob":
                continue
            path = item["path"]
            if any(path.endswith(ext) for ext in IGNORED_EXTENSIONS):
                continue
            if any(d in path.split("/") for d in IGNORED_DIRS):
                continue
            size = item.get("size", 0)
            if size > MAX_FILE_SIZE:
                continue
            files.append({"path": path, "size": size})
        return files


async def get_file_content(owner: str, name: str, path: str, branch: str) -> str:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{GITHUB_API}/repos/{owner}/{name}/contents/{path}",
            headers=_headers(),
            params={"ref": branch},
        )
        if resp.status_code != 200:
            return ""
        data = resp.json()
        if data.get("encoding") == "base64":
            import base64
            return base64.b64decode(data["content"]).decode("utf-8", errors="replace")
        return data.get("content", "")