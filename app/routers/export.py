import csv
import io
import json
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse, JSONResponse
from app.services.index_service import get_index

router = APIRouter()


@router.get("/api/export/csv")
async def export_csv(request: Request):
    index = await get_index(request)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["track_id", "track_name", "artists", "playlists", "duration_ms"])

    for track_id, track in index["tracks"].items():
        pl_names = []
        for pid in track.get("playlist_ids", []):
            pl = next((p for p in index["playlists"] if p["id"] == pid), None)
            if pl:
                pl_names.append(pl["name"])
        writer.writerow([
            track_id,
            track["name"],
            ", ".join(track.get("artist_names", [])),
            " | ".join(pl_names),
            track.get("duration_ms", 0),
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=melodex_export.csv"},
    )


@router.get("/api/export/json")
async def export_json(request: Request):
    index = await get_index(request)
    export_data = {
        "playlists": index["playlists"],
        "tracks": list(index["tracks"].values()),
        "artists": [
            {"id": a_id, **a_data}
            for a_id, a_data in index["artists"].items()
        ],
    }
    content = json.dumps(export_data, indent=2)
    return StreamingResponse(
        iter([content]),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=melodex_export.json"},
    )
