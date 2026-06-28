"""Tie lyrics + MeCab tokenization + kanji/word lookups into a response."""

from . import kanji_service, word_service
from .kana import is_kanji
from .lyrics_service import LyricsResult
from .schemas import AnalyzeResponse, Line
from .tokenizer import tokenize_line


async def analyze_lyrics(lyrics: LyricsResult) -> AnalyzeResponse:
    text = lyrics.text or ""

    # Word-level segmentation gives the contextual reading per word.
    lines = [
        Line(text=raw_line, words=tokenize_line(raw_line))
        for raw_line in text.split("\n")
    ]
    all_words = [w for line in lines for w in line.words]

    # Kanji glossary (per-character meanings, for the collapsible breakdown) and
    # the word glossary (primary). Both are fast, synchronous KanjiDic2/JMdict
    # lookups (see dictionaries.py) so they run inline on the event-loop thread.
    unique_kanji = list(dict.fromkeys(ch for ch in text if is_kanji(ch)))
    glossary = kanji_service.get_many(unique_kanji)
    word_glossary = word_service.build_word_glossary(all_words)

    return AnalyzeResponse(
        video_id=lyrics.video_id,
        title=lyrics.title,
        source=lyrics.source,
        has_lyrics=lyrics.text is not None,
        lines=lines,
        word_glossary=word_glossary,
        glossary=glossary,
    )
