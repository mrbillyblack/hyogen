"""Pydantic request/response models for the API."""

from pydantic import BaseModel, Field, model_validator


class AnalyzeRequest(BaseModel):
    """Accept either a raw videoId or a full YouTube/YT Music URL."""

    video_id: str | None = Field(default=None, alias="videoId")
    url: str | None = None

    model_config = {"populate_by_name": True}

    @model_validator(mode="after")
    def _require_one(self) -> "AnalyzeRequest":
        if not self.video_id and not self.url:
            raise ValueError("Provide either 'videoId' or 'url'.")
        return self


class SearchResult(BaseModel):
    """A single song hit from a YouTube Music search."""

    video_id: str = Field(alias="videoId")
    title: str | None = None
    artist: str | None = None
    album: str | None = None
    duration: str | None = None

    model_config = {"populate_by_name": True}


class KanjiInfo(BaseModel):
    """Readings + meanings for a single kanji, sourced from kanjiapi.dev."""

    character: str
    found: bool = True
    # All known readings rendered as hiragana (on'yomi converted from katakana).
    readings_hiragana: list[str] = []
    kun_readings: list[str] = []
    on_readings: list[str] = []
    meanings: list[str] = []
    grade: int | None = None
    jlpt: int | None = None
    stroke_count: int | None = None


class Word(BaseModel):
    """A MeCab-segmented word with its contextual reading.

    `reading` is the word's hiragana reading and is set only when the word
    contains kanji. `kanji` lists the kanji characters in the surface form;
    look them up in the response `glossary` for English meanings. `lemma` is the
    dictionary form (used to build the word glossary).
    """

    surface: str
    reading: str | None = None
    pos: str | None = None  # part of speech (UniDic pos1)
    contains_kanji: bool = False
    kanji: list[str] = []
    lemma: str | None = None
    lemma_reading: str | None = None


class Line(BaseModel):
    text: str
    words: list[Word]


class WordEntry(BaseModel):
    """A glossary entry for a whole word (e.g. 表現 → "expression").

    `kanji` are the characters in the word; look them up in the per-kanji
    `glossary` for the individual breakdown (rendered as a collapsible detail).
    """

    word: str
    reading: str | None = None
    definitions: list[str] = []
    kanji: list[str] = []


class AnalyzeResponse(BaseModel):
    video_id: str
    title: str | None = None
    source: str | None = None
    has_lyrics: bool
    lines: list[Line] = []
    # Word-level glossary (primary), ordered by first appearance.
    word_glossary: list[WordEntry] = []
    # Per-kanji glossary, for the collapsible breakdown under each word.
    glossary: dict[str, KanjiInfo] = {}
