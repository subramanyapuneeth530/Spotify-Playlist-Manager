from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from app.services.index_service import get_index, build_index
from app.services.spotify_client import spotify_delete

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/duplicates", response_class=HTMLResponse)
async def duplicates_page(request: Request):
    return templates.TemplateResponse("duplicates.html", {"request": request, "active": "duplicates"})


@router.get("/api/duplicates")
async def get_duplicates(request: Request):
    index = await get_index(request)
    dupes = []

    for track_id, track in index["tracks"].items():
        playlist_ids = track.get("playlist_ids", [])
        if len(playlist_ids) < 2:
            continue

        pl_names = []
        for pid in playlist_ids:
            pl = next((p for p in index["playlists"] if p["id"] == pid), None)
            if pl:
                pl_names.append({"id": pid, "name": pl["name"]})

        dupes.append({
            "id": track_id,
            "name": track["name"],
            "artists": track.get("artist_names", []),
            "playlist_count": len(playlist_ids),
            "playlists": pl_names,
        })

    dupes.sort(key=lambda x: x["playlist_count"], reverse=True)
    return JSONResponse(dupes)


@router.delete("/api/duplicates/{track_id}/from/{playlist_id}")
async def remove_from_playlist(request: Request, track_id: str, playlist_id: str):
    await spotify_delete(
        request,
        f"/playlists/{playlist_id}/tracks",
        payload={"tracks": [{"uri": f"spotify:track:{track_id}"}]},
    )
    # Refresh index
    await build_index(request, force=True)
    return JSONResponse({"success": True, "removed_from": playlist_id})
