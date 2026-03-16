import os
import time
import httpx
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
from app.auth.token_store import save_tokens, load_tokens, is_token_expired, clear_tokens

load_dotenv()

router = APIRouter()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8000/callback")

SCOPES = " ".join([
    "playlist-read-private",
    "playlist-read-collaborative",
    "playlist-modify-public",
    "playlist-modify-private",
    "user-read-recently-played",
    "user-read-private",
    "user-read-email",
])

AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"


@router.get("/login")
async def login(request: Request):
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES,
        "show_dialog": "false",
    }
    from urllib.parse import urlencode
    url = f"{AUTH_URL}?{urlencode(params)}"
    return RedirectResponse(url)


@router.get("/callback")
async def callback(request: Request, code: str = None, error: str = None):
    if error or not code:
        return RedirectResponse("/?error=access_denied")

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": REDIRECT_URI,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            auth=(CLIENT_ID, CLIENT_SECRET),
        )

    if resp.status_code != 200:
        return RedirectResponse("/?error=token_exchange_failed")

    data = resp.json()
    access_token = data["access_token"]
    refresh_token = data.get("refresh_token", "")
    expires_in = data.get("expires_in", 3600)

    save_tokens(access_token, refresh_token, expires_in)
    request.session["access_token"] = access_token
    request.session["refresh_token"] = refresh_token

    return RedirectResponse("/dashboard")


@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    clear_tokens()
    return RedirectResponse("/")


async def get_valid_token(request: Request) -> str:
    """Returns a valid access token, refreshing if needed."""
    if not is_token_expired():
        tokens = load_tokens()
        if tokens:
            return tokens["access_token"]

    tokens = load_tokens()
    refresh_token = tokens.get("refresh_token") if tokens else request.session.get("refresh_token")

    if not refresh_token:
        raise Exception("No refresh token available. Please log in again.")

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            auth=(CLIENT_ID, CLIENT_SECRET),
        )

    if resp.status_code != 200:
        raise Exception("Token refresh failed. Please log in again.")

    data = resp.json()
    new_access = data["access_token"]
    new_refresh = data.get("refresh_token", refresh_token)
    expires_in = data.get("expires_in", 3600)

    save_tokens(new_access, new_refresh, expires_in)
    request.session["access_token"] = new_access
    request.session["refresh_token"] = new_refresh

    return new_access
