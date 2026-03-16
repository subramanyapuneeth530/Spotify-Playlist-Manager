from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from app.services.artist_service import get_artist_cards, get_genre_breakdown
from app.services.playlist_service import create_artist_playlist
from app.services.index_service import get_index, build_index

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/artists", response_class=HTMLResponse)
async def artists_page(request: Request):
    return templates.TemplateResponse("artists.html", {"request": request, "active": "artists"})


@router.get("/api/artists")
async def api_artists(request: Request, q: str = Query(None)):
    cards = await get_artist_cards(request)
    if q:
        cards = [c for c in cards if q.lower() in c["name"].lower()]
    return JSONResponse(cards)


@router.get("/api/genres")
async def api_genres(request: Request):
    genres = await get_genre_breakdown(request)
    return JSONResponse(genres)


@router.post("/api/artists/{artist_id}/create-playlist")
async def create_playlist(
    request: Request,
    artist_id: str,
    name: str = Query(None),
    public: bool = Query(False),
):
    result = await create_artist_playlist(request, artist_id, name=name, public=public)
    # Invalidate cache so new playlist appears
    await build_index(request, force=True)
    return JSONResponse(result)


@router.get("/api/artist/{artist_id}/tracks")
async def artist_tracks(request: Request, artist_id: str):
    index = await get_index(request)
    artist = index["artists"].get(artist_id)
    if not artist:
        return JSONResponse({"error": "Artist not found"}, status_code=404)
    tracks = [index["tracks"].get(tid) for tid in artist["track_ids"] if index["tracks"].get(tid)]
    return JSONResponse({
        "artist": artist,
        "tracks": tracks,
    })
