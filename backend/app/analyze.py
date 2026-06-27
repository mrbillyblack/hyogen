"""Tie lyrics + MeCab tokenization + kanji lookup into an annotated response."""

from sqlalchemy.ext.asyncio import AsyncSession

from . import kanji_service
from .kana import is_kanji
from .lyrics_service import LyricsResult
from .schemas import AnalyzeResponse, KanjiInfo, Line
from .tokenizer import tokenize_line


async def analyze_lyrics(
    session: AsyncSession, lyrics: LyricsResult
) -> AnalyzeResponse:
    text = lyrics.text or ""

    # Collect every unique kanji in the song, then resolve them in one pass.
    unique_kanji = list(dict.fromkeys(ch for ch in text if is_kanji(ch)))
    glossary: dict[str, KanjiInfo] = await kanji_service.get_many(
        session, unique_kanji
    )

    # Word-level segmentation gives the contextual reading per word; the
    # glossary supplies English meanings per kanji.
    lines = [
        Line(text=raw_line, words=tokenize_line(raw_line))
        for raw_line in text.split("\n")
    ]

    return AnalyzeResponse(
        video_id=lyrics.video_id,
        title=lyrics.title,
        source=lyrics.source,
        has_lyrics=lyrics.text is not None,
        lines=lines,
        glossary=glossary,
    )
