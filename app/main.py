from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
import os
from dotenv import load_dotenv

from app.routers import playlists, artists, analytics, duplicates, history, export
from app.auth.spotify_auth import router as auth_router

load_dotenv()

app = FastAPI(title="Melodex", description="Spotify Playlist Manager")

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET", "fallback-secret-change-me"),
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

app.include_router(auth_router)
app.include_router(playlists.router)
app.include_router(artists.router)
app.include_router(analytics.router)
app.include_router(duplicates.router)
app.include_router(history.router)
app.include_router(export.router)


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    token = request.session.get("access_token")
    if not token:
        return templates.TemplateResponse("login.html", {"request": request})
    return templates.TemplateResponse("index.html", {"request": request})


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return templates.TemplateResponse(
        "error.html",
        {"request": request, "error": str(exc)},
        status_code=500,
    )
