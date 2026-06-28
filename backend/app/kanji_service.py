"""Per-kanji readings + meanings from KanjiDic2 (bundled with jamdict).

This is fully offline — the dataset ships in `jamdict-data` inside the image, so
there's no kanjiapi.dev calls and no database. KanjiDic2 is the same source
kanjiapi.dev is built from, so the data is equivalent.
"""

from .dictionaries import jam
from .kana import katakana_to_hiragana
from .schemas import KanjiInfo


def _to_info(char: str, entry) -> KanjiInfo:
    """Convert a KanjiDic2 character entry to our KanjiInfo schema."""
    if entry is None:
        return KanjiInfo(character=char, found=False)

    kun: list[str] = []
    on: list[str] = []
    meanings: list[str] = []
    for group in entry.rm_groups:
        for r in group.readings:
            if r.r_type == "ja_kun":
                kun.append(r.value)
            elif r.r_type == "ja_on":
                on.append(r.value)
        for m in group.meanings:
            # KanjiDic2 leaves m_lang empty for English meanings.
            if not m.m_lang or m.m_lang == "en":
                meanings.append(m.value)

    # Deduped hiragana reading list: kun as-is, on converted from katakana.
    # Strip okurigana/affix markers (e.g. "あらわ.す", "-おもて").
    seen: set[str] = set()
    readings_hiragana: list[str] = []
    for r in [*kun, *(katakana_to_hiragana(o) for o in on)]:
        clean = r.replace(".", "").replace("-", "").replace("ー", "")
        if clean and clean not in seen:
            seen.add(clean)
            readings_hiragana.append(clean)

    return KanjiInfo(
        character=char,
        found=True,
        readings_hiragana=readings_hiragana,
        kun_readings=kun,
        on_readings=on,
        meanings=meanings,
        grade=entry.grade,
        jlpt=entry.jlpt,
        stroke_count=entry.stroke_count,
    )


def _lookup(char: str) -> KanjiInfo:
    chars = jam.lookup(char).chars
    entry = next((c for c in chars if c.literal == char), None)
    return _to_info(char, entry)


def get_many(chars: list[str]) -> dict[str, KanjiInfo]:
    """Resolve a set of kanji characters to readings + meanings."""
    if not chars:
        return {}
    return {ch: _lookup(ch) for ch in dict.fromkeys(chars)}


def get_one(char: str) -> KanjiInfo:
    return get_many([char])[char]
