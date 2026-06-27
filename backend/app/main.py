"""FastAPI application for Hyogen — annotate Japanese lyrics with kanji readings."""

import re
from contextlib import asynccontextmanager
from urllib.parse import quote

from fastapi import Depends, FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from . import anki_service, kanji_service
from .analyze import analyze_lyrics
from .config import settings
from .db import get_session, init_db
from .lyrics_service import extract_video_id, fetch_lyrics, search_songs
from .schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    AnkiRequest,
    KanjiInfo,
    SearchResult,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="Hyogen", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/search", response_model=list[SearchResult])
async def search(q: str, limit: int = 10) -> list[SearchResult]:
    """Search YouTube Music for songs matching `q`."""
    if not q.strip():
        raise HTTPException(status_code=400, detail="Query 'q' must not be empty.")
    try:
        hits = await search_songs(q, limit)
    except Exception as exc:
        raise HTTPException(
            status_code=502, detail=f"Search failed: {exc}"
        ) from exc
    return [SearchResult(**h) for h in hits]


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze(
    req: AnalyzeRequest, session: AsyncSession = Depends(get_session)
) -> AnalyzeResponse:
    """Fetch a song's lyrics and annotate every kanji with readings + meanings."""
    raw = req.video_id or req.url or ""
    try:
        video_id = extract_video_id(raw)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        lyrics = await fetch_lyrics(video_id)
    except Exception as exc:  # ytmusicapi raises various error types
        raise HTTPException(
            status_code=502, detail=f"Failed to fetch lyrics: {exc}"
        ) from exc

    return await analyze_lyrics(session, lyrics)


@app.post("/api/anki")
async def anki(req: AnkiRequest) -> Response:
    """Build an Anki deck (.apkg) from a song's word glossary."""
    if not req.words:
        raise HTTPException(status_code=400, detail="No glossary words provided.")
    data = anki_service.build_deck(req.title, req.words)
    # HTTP headers are latin-1, but titles can be Japanese. Provide an ASCII
    # fallback filename plus an RFC 5987 UTF-8 name for capable clients.
    ascii_base = re.sub(r"[^A-Za-z0-9._ -]+", "", req.title or "").strip()
    ascii_name = f"{ascii_base or 'hyogen'}.apkg"
    utf8_name = quote(f"{req.title or 'hyogen'}.apkg")
    return Response(
        content=data,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": (
                f'attachment; filename="{ascii_name}"; '
                f"filename*=UTF-8''{utf8_name}"
            )
        },
    )


@app.get("/api/kanji/{char}", response_model=KanjiInfo)
async def kanji(
    char: str, session: AsyncSession = Depends(get_session)
) -> KanjiInfo:
    """Look up a single kanji (lazy-cached from kanjiapi.dev)."""
    if len(char) != 1:
        raise HTTPException(status_code=400, detail="Provide exactly one character.")
    return await kanji_service.get_one(session, char)
