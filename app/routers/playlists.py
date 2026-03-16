from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List
from app.services.index_service import get_index, build_index, index_cache_age
from app.services.playlist_service import merge_playlists

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "active": "dashboard"})


@router.get("/playlists", response_class=HTMLResponse)
async def playlists_page(request: Request):
    index = await get_index(request)
    playlists = index["playlists"]
    return templates.TemplateResponse("playlists.html", {
        "request": request,
        "playlists": playlists,
        "total": len(playlists),
        "active": "playlists",
    })


@router.get("/api/index")
async def get_full_index(request: Request, force: bool = False):
    index = await build_index(request, force=force)
    age = index_cache_age()
    return JSONResponse({
        "playlists": index["playlists"],
        "artist_count": len(index["artists"]),
        "track_count": len(index["tracks"]),
        "cache_age_seconds": round(age, 0) if age is not None else None,
    })


@router.get("/api/playlists")
async def api_playlists(
    request: Request,
    q: str = Query(None),
    type: str = Query(None),
    sort: str = Query("name"),
):
    index = await get_index(request)
    playlists = list(index["playlists"])

    if q:
        playlists = [p for p in playlists if q.lower() in p["name"].lower()]
    if type == "artist":
        playlists = [p for p in playlists if "— all tracks" in p["name"]]
    elif type == "manual":
        playlists = [p for p in playlists if "— all tracks" not in p["name"]]

    if sort == "name":
        playlists.sort(key=lambda x: x["name"].lower())
    elif sort == "tracks":
        playlists.sort(key=lambda x: x["total"], reverse=True)

    return JSONResponse(playlists)


@router.get("/api/playlist/{playlist_id}/tracks")
async def playlist_tracks(request: Request, playlist_id: str):
    index = await get_index(request)
    track_ids = index["playlist_track_map"].get(playlist_id, [])
    tracks = [index["tracks"].get(tid) for tid in track_ids if index["tracks"].get(tid)]
    return JSONResponse(tracks)


class MergeRequest(BaseModel):
    playlist_ids: List[str]
    name: str
    public: bool = False


@router.get("/create", response_class=HTMLResponse)
async def create_page(request: Request):
    return templates.TemplateResponse("create.html", {"request": request, "active": "create"})


@router.post("/api/playlists/merge")
async def merge(request: Request, body: MergeRequest):
    try:
        result = await merge_playlists(request, body.playlist_ids, body.name, body.public)
        return JSONResponse(result)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)
