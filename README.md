# Melodex — Spotify Playlist Manager

A local web app that analyses your Spotify library, groups tracks by artist, detects duplicates, visualises your listening history, and creates artist-only playlists from songs you already have.

## Features

- **Dashboard** — total tracks, artists, hours of music, health score, overlap matrix
- **Playlists** — browse, filter (all / artist-only / manual), sort, merge with deduplication
- **Artists** — card grid with genres, track previews, per-artist track drawer, create playlists
- **Analytics** — top-artist chart, playlist size chart, genre donut, library health score
- **Duplicates** — detect tracks in multiple playlists, remove from specific playlists
- **History** — recently played timeline, most-replayed tracks (Spotify Premium)
- **Create** — single artist playlist or bulk-create for top N artists
- **Export** — download full index as CSV or JSON
- **5 Themes** — Cyber, Paper, Aurora, Obsidian, Chalk
- **Keyboard shortcuts** — press `?` to view all shortcuts
- **Persistent cache** — SQLite-backed index survives server restarts with TTL
- **Auto token refresh** — Spotify access token refreshed silently before expiry

## Requirements

- Python 3.11+
- Spotify Premium account
- Spotify Developer App (free to create)

## Setup

### 1. Create a Spotify App

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new app
3. Add Redirect URI: `http://127.0.0.1:8000/callback`
4. Note your **Client ID** and **Client Secret**

### 2. Configure environment

```bash
cp .env.example .env
# Fill in your SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, and SESSION_SECRET
```

### 3. Install and run

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

pip install -r requirements.txt
python run.py
```

Open: http://127.0.0.1:8000

## Environment variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `SPOTIFY_CLIENT_ID` | Yes | — | From Spotify Developer Dashboard |
| `SPOTIFY_CLIENT_SECRET` | Yes | — | From Spotify Developer Dashboard |
| `SPOTIFY_REDIRECT_URI` | No | `http://127.0.0.1:8000/callback` | Must match Spotify app settings |
| `SESSION_SECRET` | Yes | — | Any long random string |
| `HOST` | No | `127.0.0.1` | Server host |
| `PORT` | No | `8000` | Server port |
| `CACHE_TTL_SECONDS` | No | `3600` | How long to cache the library index |

## Keyboard shortcuts

| Key | Action |
|---|---|
| `g d` | Go to Dashboard |
| `g p` | Go to Playlists |
| `g a` | Go to Artists |
| `g n` | Go to Analytics |
| `g u` | Go to Duplicates |
| `g h` | Go to History |
| `/` | Focus search |
| `?` | Show shortcuts panel |

## Notes

- Large libraries (500+ playlists) take time to index on first run due to Spotify API pagination
- The index is cached in SQLite and reused until TTL expires or you force-refresh
- Audio Features (BPM, energy, mood) are unavailable — Spotify deprecated this endpoint in Nov 2024
- Track previews (30s) may be `null` for some tracks — Spotify no longer guarantees preview URLs
