from fastapi import Request
from app.services.spotify_client import paginate, spotify_get
from app.cache.cache_manager import get_cache, set_cache, get_cache_age

CACHE_KEY = "global_index"


async def build_index(request: Request, force: bool = False) -> dict:
    """Build or return cached global index: artists → tracks, tracks → playlists."""
    if not force:
        cached = get_cache(CACHE_KEY)
        if cached:
            return cached

    # Fetch all playlists
    playlists_raw = await paginate(request, "/me/playlists")
    playlists = []
    artist_index = {}   # artist_id -> {name, track_ids, playlist_ids, image}
    track_index = {}    # track_id -> {name, artist_ids, playlist_ids, duration_ms, preview_url}
    playlist_track_map = {}  # playlist_id -> [track_ids]

    for pl in playlists_raw:
        if not pl or not pl.get("id"):
            continue
        pl_id = pl["id"]
        pl_name = pl.get("name", "Untitled")
        pl_image = (pl.get("images") or [{}])[0].get("url", "")
        pl_tracks_total = (pl.get("tracks") or {}).get("total", 0)

        playlists.append({
            "id": pl_id,
            "name": pl_name,
            "image": pl_image,
            "total": pl_tracks_total,
            "owner": (pl.get("owner") or {}).get("display_name", ""),
            "public": pl.get("public", False),
        })

        # Fetch all tracks for this playlist
        tracks_raw = await paginate(request, f"/playlists/{pl_id}/tracks")
        playlist_track_map[pl_id] = []

        for item in tracks_raw:
            track = item.get("track")
            if not track or not track.get("id"):
                continue
            t_id = track["id"]
            t_name = track.get("name", "Unknown")
            t_duration = track.get("duration_ms", 0)
            t_preview = track.get("preview_url")
            artists = track.get("artists", [])

            playlist_track_map[pl_id].append(t_id)

            # Update track index
            if t_id not in track_index:
                track_index[t_id] = {
                    "id": t_id,
                    "name": t_name,
                    "duration_ms": t_duration,
                    "preview_url": t_preview,
                    "artist_ids": [a["id"] for a in artists if a.get("id")],
                    "artist_names": [a["name"] for a in artists if a.get("name")],
                    "playlist_ids": [],
                }
            if pl_id not in track_index[t_id]["playlist_ids"]:
                track_index[t_id]["playlist_ids"].append(pl_id)

            # Update artist index
            for artist in artists:
                a_id = artist.get("id")
                a_name = artist.get("name")
                if not a_id:
                    continue
                if a_id not in artist_index:
                    artist_index[a_id] = {
                        "id": a_id,
                        "name": a_name,
                        "track_ids": [],
                        "playlist_ids": [],
                        "genres": [],
                    }
                if t_id not in artist_index[a_id]["track_ids"]:
                    artist_index[a_id]["track_ids"].append(t_id)
                if pl_id not in artist_index[a_id]["playlist_ids"]:
                    artist_index[a_id]["playlist_ids"].append(pl_id)

    index = {
        "playlists": playlists,
        "artists": artist_index,
        "tracks": track_index,
        "playlist_track_map": playlist_track_map,
    }

    set_cache(CACHE_KEY, index)
    return index


async def get_index(request: Request) -> dict:
    cached = get_cache(CACHE_KEY)
    if cached:
        return cached
    return await build_index(request)


def index_cache_age():
    return get_cache_age(CACHE_KEY)
