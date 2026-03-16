from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from app.services.history_service import get_recently_played, get_repeat_tracks, get_timeline

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/history", response_class=HTMLResponse)
async def history_page(request: Request):
    return templates.TemplateResponse("history.html", {"request": request, "active": "history"})


@router.get("/api/history/recent")
async def recent(request: Request):
    tracks = await get_recently_played(request)
    return JSONResponse(tracks)


@router.get("/api/history/repeats")
async def repeats(request: Request):
    tracks = await get_repeat_tracks(request)
    return JSONResponse(tracks)


@router.get("/api/history/timeline")
async def timeline(request: Request):
    data = await get_timeline(request)
    return JSONResponse(data)
