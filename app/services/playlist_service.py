from fastapi import Request
from typing import List
from app.services.spotify_client import spotify_post, spotify_get, paginate
from app.services.index_service import get_index
import os


async def get_current_user_id(request: Request) -> str:
    data = await spotify_get(request, "/me")
    return data["id"]


async def create_artist_playlist(
    request: Request,
    artist_id: str,
    name: str = None,
    public: bool = False,
) -> dict:
    index = await get_index(request)
    artist = index["artists"].get(artist_id)
    if not artist:
        raise Exception(f"Artist {artist_id} not found in index")

    pl_name = name or f"{artist['name']} — all tracks"

    # Guard: check if playlist with same name already exists
    existing = [p for p in index["playlists"] if p["name"].lower() == pl_name.lower()]
    if existing:
        raise Exception(f"Playlist '{pl_name}' already exists")

    user_id = await get_current_user_id(request)
    new_pl = await spotify_post(request, f"/users/{user_id}/playlists", {
        "name": pl_name,
        "public": public,
        "description": f"Auto-created by Melodex — all {artist['name']} tracks from your library",
    })

    pl_id = new_pl["id"]
    track_uris = [f"spotify:track:{tid}" for tid in artist["track_ids"]]

    # Add tracks in batches of 100
    for i in range(0, len(track_uris), 100):
        batch = track_uris[i:i+100]
        await spotify_post(request, f"/playlists/{pl_id}/tracks", {"uris": batch})

    return {"playlist_id": pl_id, "name": pl_name, "track_count": len(track_uris)}


async def merge_playlists(
    request: Request,
    playlist_ids: List[str],
    name: str,
    public: bool = False,
) -> dict:
    """Merge multiple playlists, deduplicating tracks."""
    index = await get_index(request)
    seen = set()
    track_uris = []

    for pl_id in playlist_ids:
        for t_id in index["playlist_track_map"].get(pl_id, []):
            if t_id not in seen:
                seen.add(t_id)
                track_uris.append(f"spotify:track:{t_id}")

    user_id = await get_current_user_id(request)
    new_pl = await spotify_post(request, f"/users/{user_id}/playlists", {
        "name": name,
        "public": public,
        "description": "Merged playlist created by Melodex",
    })
    pl_id = new_pl["id"]

    for i in range(0, len(track_uris), 100):
        batch = track_uris[i:i+100]
        await spotify_post(request, f"/playlists/{pl_id}/tracks", {"uris": batch})

    return {"playlist_id": pl_id, "name": name, "track_count": len(track_uris)}
