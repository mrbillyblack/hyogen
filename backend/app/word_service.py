"""Word-level English definitions from JMdict via jamdict (offline SQLite).

jamdict is synchronous and ships its own bundled dictionary, so we build the
whole word glossary in a single thread-pool call (one jamdict instance, used
serially — no concurrency concerns).
"""

from .dictionaries import jam
from .schemas import Word, WordEntry


def _glosses_for(lemma: str, surface: str, reading: str | None) -> list[str]:
    """Look up a word and return its English glosses.

    Prefers the JMdict entry whose kana reading matches MeCab's contextual
    reading (so 回る → まわる "to turn", not めぐる "to go around").
    """
    result = jam.lookup(lemma)
    if not result.entries and surface != lemma:
        result = jam.lookup(surface)
    if not result.entries:
        return []

    chosen = result.entries[0]
    if reading:
        for entry in result.entries:
            if any(k.text == reading for k in entry.kana_forms):
                chosen = entry
                break

    glosses: list[str] = []
    for sense in chosen.senses:
        for gloss in sense.gloss:
            text = str(gloss)
            if text and text not in glosses:
                glosses.append(text)
    return glosses


def build_word_glossary(words: list[Word]) -> list[WordEntry]:
    seen: set[str] = set()
    entries: list[WordEntry] = []
    for w in words:
        if not w.contains_kanji:
            continue
        key = w.lemma or w.surface
        if key in seen:
            continue
        seen.add(key)
        glosses = _glosses_for(key, w.surface, w.lemma_reading)
        entries.append(
            WordEntry(
                word=key,
                reading=w.lemma_reading,
                definitions=glosses[:6],
                kanji=list(dict.fromkeys(w.kanji)),
            )
        )
    return entries
