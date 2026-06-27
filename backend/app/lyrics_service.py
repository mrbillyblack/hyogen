"""Fetch lyrics from YouTube Music via the vendored ytmusicapi fork.

ytmusicapi is synchronous (requests-based), so calls are dispatched to a thread
pool to avoid blocking the event loop. No auth is needed for public lyrics.
"""

import re
from dataclasses import dataclass
from urllib.parse import parse_qs, urlparse

from fastapi.concurrency import run_in_threadpool
from ytmusicapi import YTMusic

# A single unauthenticated client is reused across requests.
_yt = YTMusic()


@dataclass
class LyricsResult:
    video_id: str
    title: str | None
    source: str | None
    text: str | None  # None when the song has no lyrics


def extract_video_id(value: str) -> str:
    """Accept a raw videoId or any YouTube/YT Music URL and return the id."""
    value = value.strip()
    if "youtube.com" in value or "youtu.be" in value or value.startswith("http"):
        parsed = urlparse(value)
        if parsed.hostname and "youtu.be" in parsed.hostname:
            vid = parsed.path.lstrip("/")
            if vid:
                return vid
        qs = parse_qs(parsed.query)
        if "v" in qs and qs["v"]:
            return qs["v"][0]
    # Already looks like a bare id.
    if re.fullmatch(r"[\w-]{6,}", value):
        return value
    raise ValueError(f"Could not extract a video id from {value!r}")


def _fetch_sync(video_id: str) -> LyricsResult:
    watch = _yt.get_watch_playlist(videoId=video_id)
    title = None
    tracks = watch.get("tracks") or []
    if tracks:
        title = tracks[0].get("title")

    browse_id = watch.get("lyrics")
    if not browse_id:
        return LyricsResult(video_id, title, None, None)

    lyrics = _yt.get_lyrics(browse_id)
    if not lyrics:
        return LyricsResult(video_id, title, None, None)

    return LyricsResult(
        video_id=video_id,
        title=title,
        source=lyrics.get("source"),
        text=lyrics.get("lyrics"),
    )


async def fetch_lyrics(video_id: str) -> LyricsResult:
    return await run_in_threadpool(_fetch_sync, video_id)


def _search_sync(query: str, limit: int) -> list[dict]:
    results = _yt.search(query, filter="songs", limit=limit)
    songs: list[dict] = []
    for r in results:
        video_id = r.get("videoId")
        if not video_id:
            continue
        artists = ", ".join(a.get("name", "") for a in (r.get("artists") or []))
        album = r.get("album")
        songs.append(
            {
                "videoId": video_id,
                "title": r.get("title"),
                "artist": artists or None,
                "album": album.get("name") if isinstance(album, dict) else None,
                "duration": r.get("duration"),
            }
        )
    return songs


async def search_songs(query: str, limit: int = 10) -> list[dict]:
    return await run_in_threadpool(_search_sync, query, limit)
