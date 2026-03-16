from fastapi import Request
from app.services.spotify_client import spotify_get
from app.services.index_service import get_index
from app.cache.cache_manager import get_cache, set_cache

GENRE_CACHE_KEY = "artist_genres"


async def enrich_artists_with_genres(request: Request) -> dict:
    """Fetch genre data for all artists in the index. Cached separately."""
    cached = get_cache(GENRE_CACHE_KEY)
    if cached:
        return cached

    index = await get_index(request)
    artist_ids = list(index["artists"].keys())
    genre_map = {}

    # Spotify allows up to 50 artists per request
    for i in range(0, len(artist_ids), 50):
        batch = artist_ids[i:i+50]
        params = {"ids": ",".join(batch)}
        data = await spotify_get(request, "/artists", params=params)
        for artist in data.get("artists") or []:
            if artist and artist.get("id"):
                genre_map[artist["id"]] = {
                    "genres": artist.get("genres", []),
                    "image": (artist.get("images") or [{}])[0].get("url", ""),
                    "popularity": artist.get("popularity", 0),
                }

    set_cache(GENRE_CACHE_KEY, genre_map, ttl=86400)
    return genre_map


async def get_genre_breakdown(request: Request) -> list[dict]:
    """Return sorted list of genres with track counts."""
    index = await get_index(request)
    genre_map = await enrich_artists_with_genres(request)
    genre_counts = {}

    for artist_id, artist in index["artists"].items():
        artist_genres = genre_map.get(artist_id, {}).get("genres", [])
        track_count = len(artist["track_ids"])
        for genre in artist_genres:
            genre_counts[genre] = genre_counts.get(genre, 0) + track_count

    return sorted(
        [{"genre": g, "count": c} for g, c in genre_counts.items()],
        key=lambda x: x["count"],
        reverse=True,
    )[:20]


async def get_artist_cards(request: Request) -> list[dict]:
    """Return enriched artist list sorted by track count."""
    index = await get_index(request)
    genre_map = await enrich_artists_with_genres(request)
    cards = []

    for artist_id, artist in index["artists"].items():
        enriched = genre_map.get(artist_id, {})
        cards.append({
            "id": artist_id,
            "name": artist["name"],
            "track_count": len(artist["track_ids"]),
            "playlist_count": len(artist["playlist_ids"]),
            "genres": enriched.get("genres", [])[:3],
            "image": enriched.get("image", ""),
            "popularity": enriched.get("popularity", 0),
        })

    return sorted(cards, key=lambda x: x["track_count"], reverse=True)
