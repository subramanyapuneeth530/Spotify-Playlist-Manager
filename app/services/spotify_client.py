import httpx
import asyncio
import logging
from fastapi import Request
from app.auth.spotify_auth import get_valid_token

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

BASE = "https://api.spotify.com/v1"
MAX_RETRIES = 3
TIMEOUT = httpx.Timeout(10.0, connect=5.0)


async def spotify_get(request: Request, path: str, params: dict = None) -> dict:
    token = await get_valid_token(request)
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{BASE}{path}"
    logger.info(f"Spotify GET {path} params={params}")

    for attempt in range(MAX_RETRIES):
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                resp = await client.get(url, headers=headers, params=params)
        except httpx.TimeoutException:
            logger.warning(f"Timeout on {path} attempt {attempt+1}")
            await asyncio.sleep(2)
            continue
        except httpx.RequestError as e:
            logger.error(f"Request error on {path}: {e}")
            raise

        logger.info(f"  -> {resp.status_code}")
        if resp.status_code == 200:
            return resp.json()
        elif resp.status_code == 429:
            retry_after = int(resp.headers.get("Retry-After", 2))
            logger.warning(f"Rate limited, waiting {retry_after}s")
            await asyncio.sleep(retry_after)
        elif resp.status_code == 401:
            logger.warning("Token expired, refreshing...")
            token = await get_valid_token(request)
            headers["Authorization"] = f"Bearer {token}"
        else:
            logger.error(f"Spotify error {resp.status_code}: {resp.text}")
            resp.raise_for_status()

    raise Exception(f"Spotify API request failed after {MAX_RETRIES} retries: {path}")


async def spotify_post(request: Request, path: str, payload: dict = None) -> dict:
    token = await get_valid_token(request)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    url = f"{BASE}{path}"

    async with httpx.AsyncClient() as client:
        resp = await client.post(url, headers=headers, json=payload or {}, timeout=15)

    if resp.status_code in (200, 201):
        return resp.json() if resp.content else {}
    resp.raise_for_status()


async def spotify_delete(request: Request, path: str, payload: dict = None) -> dict:
    token = await get_valid_token(request)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    url = f"{BASE}{path}"

    async with httpx.AsyncClient() as client:
        resp = await client.request(
            "DELETE", url, headers=headers, json=payload or {}, timeout=15
        )

    if resp.status_code in (200, 204):
        return resp.json() if resp.content else {}
    resp.raise_for_status()


async def paginate(request: Request, path: str, params: dict = None, key: str = "items") -> list:
    """Fetch all pages from a paginated Spotify endpoint."""
    results = []
    p = dict(params or {})
    p.setdefault("limit", 50)
    p["offset"] = 0

    while True:
        data = await spotify_get(request, path, params=p)
        items = data.get(key) or data.get("items", [])
        results.extend(items)
        total = data.get("total", 0)
        p["offset"] += len(items)
        if p["offset"] >= total or not items:
            break

    return results
