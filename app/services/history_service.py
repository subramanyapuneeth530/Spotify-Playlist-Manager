from fastapi import Request
from app.services.spotify_client import spotify_get
from app.cache.cache_manager import get_cache, set_cache
from collections import Counter
import time

HISTORY_CACHE_KEY = "recently_played"


async def get_recently_played(request: Request, limit: int = 50) -> list[dict]:
    cached = get_cache(HISTORY_CACHE_KEY)
    if cached:
        return cached

    data = await spotify_get(request, "/me/player/recently-played", params={"limit": limit})
    items = data.get("items", [])

    tracks = []
    for item in items:
        track = item.get("track")
        if not track:
            continue
        tracks.append({
            "id": track.get("id"),
            "name": track.get("name"),
            "artists": [a["name"] for a in track.get("artists", [])],
            "played_at": item.get("played_at"),
            "duration_ms": track.get("duration_ms", 0),
            "preview_url": track.get("preview_url"),
            "album_image": (track.get("album", {}).get("images") or [{}])[0].get("url", ""),
        })

    set_cache(HISTORY_CACHE_KEY, tracks, ttl=300)
    return tracks


async def get_repeat_tracks(request: Request) -> list[dict]:
    """Find tracks that appear multiple times in recent history."""
    history = await get_recently_played(request)
    counts = Counter(t["id"] for t in history if t.get("id"))
    repeats = {t_id: count for t_id, count in counts.items() if count > 1}

    seen = set()
    result = []
    for track in history:
        t_id = track.get("id")
        if t_id in repeats and t_id not in seen:
            seen.add(t_id)
            result.append({**track, "play_count": repeats[t_id]})

    return sorted(result, key=lambda x: x["play_count"], reverse=True)


async def get_timeline(request: Request) -> list[dict]:
    """Group recently played tracks by date."""
    history = await get_recently_played(request)
    by_date = {}
    for track in history:
        date = (track.get("played_at") or "")[:10]
        if not date:
            continue
        if date not in by_date:
            by_date[date] = []
        by_date[date].append(track)

    return [
        {"date": date, "tracks": tracks, "count": len(tracks)}
        for date, tracks in sorted(by_date.items(), reverse=True)
    ]
