from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from app.services.index_service import get_index, index_cache_age
from app.services.spotify_client import spotify_get

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/analytics", response_class=HTMLResponse)
async def analytics_page(request: Request):
    return templates.TemplateResponse("analytics.html", {"request": request, "active": "analytics"})


@router.get("/api/analytics/summary")
async def summary(request: Request):
    index = await get_index(request)
    playlists = index["playlists"]
    tracks = index["tracks"]
    artists = index["artists"]
    ptmap = index["playlist_track_map"]

    total_duration_ms = sum(t.get("duration_ms", 0) for t in tracks.values())
    total_duration_hrs = round(total_duration_ms / 3_600_000, 1)

    # Overlap matrix: tracks in N playlists
    overlap = {1: 0, 2: 0, 3: 0, 4: 0}
    for track in tracks.values():
        n = len(track.get("playlist_ids", []))
        if n >= 4:
            overlap[4] = overlap.get(4, 0) + 1
        elif n >= 1:
            overlap[n] = overlap.get(n, 0) + 1

    # Top artists
    top_artists = sorted(
        [{"name": a["name"], "track_count": len(a["track_ids"])} for a in artists.values()],
        key=lambda x: x["track_count"],
        reverse=True,
    )[:10]

    # Playlist sizes
    playlist_sizes = sorted(
        [{"name": p["name"], "total": p["total"]} for p in playlists],
        key=lambda x: x["total"],
        reverse=True,
    )[:10]

    # Health score: penalise duplicates and low variety
    dup_count = sum(1 for t in tracks.values() if len(t.get("playlist_ids", [])) > 1)
    variety = len(artists) / max(len(tracks), 1)
    dup_penalty = min(dup_count * 2, 30)
    health = max(0, min(100, int(70 * variety * 10 + 30 - dup_penalty)))

    age = index_cache_age()

    return JSONResponse({
        "total_playlists": len(playlists),
        "total_tracks": len(tracks),
        "unique_artists": len(artists),
        "total_duration_hrs": total_duration_hrs,
        "duplicate_count": dup_count,
        "health_score": health,
        "overlap": overlap,
        "top_artists": top_artists,
        "playlist_sizes": playlist_sizes,
        "cache_age_seconds": round(age, 0) if age is not None else None,
    })


@router.get("/api/user")
async def get_user(request: Request):
    data = await spotify_get(request, "/me")
    # Spotify can return null for display_name — fall back to email prefix
    display_name = data.get("display_name") or ""
    email = data.get("email") or ""
    email_prefix = email.split("@")[0] if email else ""
    images = data.get("images") or []
    # Prefer the smallest image for the avatar (last in list) or first if only one
    image_url = images[-1].get("url", "") if images else ""
    return JSONResponse({
        "display_name": display_name,
        "email_prefix": email_prefix,
        "image": image_url,
        "plan": data.get("product", ""),
    })
