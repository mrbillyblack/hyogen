"""Word-level tokenization via MeCab (fugashi + unidic-lite).

A per-character kanji lookup can only list every *possible* reading. MeCab
segments a line into words and gives the one reading actually used in context,
which is what furigana needs.

Readings come from UniDic's ``kana`` field — the kana spelling (東京 →
トウキョウ) rather than ``pron``, which is phonetic (東京 → トーキョー) and
awkward to render as furigana — then folded to hiragana.

The tagger is created once. MeCab's tagger is not thread-safe, so callers run
tokenization synchronously on the event-loop thread (lyrics are small and this
is sub-millisecond per line).
"""

import fugashi

from .kana import is_kanji, katakana_to_hiragana
from .schemas import Word

_tagger = fugashi.Tagger()


def tokenize_line(line: str) -> list[Word]:
    """Split one lyric line into words, attaching a reading to kanji-bearing ones."""
    if not line.strip():
        return []

    words: list[Word] = []
    cursor = 0
    for node in _tagger(line):
        surface = node.surface
        if not surface:
            continue

        # MeCab drops inter-token whitespace, which makes English lines run
        # together ("Bad example" → "Badexample"). Align each surface back to
        # the original line and re-insert any skipped characters as their own
        # token so the original spacing survives.
        idx = line.find(surface, cursor)
        if idx == -1:
            idx = cursor
        if idx > cursor:
            words.append(Word(surface=line[cursor:idx], contains_kanji=False))
        cursor = idx + len(surface)

        kanji_chars = [c for c in surface if is_kanji(c)]
        contains = bool(kanji_chars)

        reading: str | None = None
        if contains:
            kana = getattr(node.feature, "kana", None)
            if kana and kana != "*":
                reading = katakana_to_hiragana(kana)

        pos = getattr(node.feature, "pos1", None)
        if pos == "*":
            pos = None

        # Dictionary form + its reading, used to look up word definitions and to
        # disambiguate which JMdict sense applies (e.g. 回る → まわる, not めぐる).
        lemma = getattr(node.feature, "lemma", None)
        if lemma == "*":
            lemma = None
        elif lemma:
            # UniDic appends a disambiguation tag to some lemmas (e.g.
            # "引く-他動詞"); strip it for clean lookup/display. The tag uses an
            # ASCII hyphen, distinct from the chōonpu ー used inside words.
            lemma = lemma.split("-", 1)[0]
        lemma_reading: str | None = None
        if contains:
            kana_base = getattr(node.feature, "kanaBase", None)
            if kana_base and kana_base != "*":
                lemma_reading = katakana_to_hiragana(kana_base)

        words.append(
            Word(
                surface=surface,
                reading=reading,
                pos=pos,
                contains_kanji=contains,
                kanji=kanji_chars,
                lemma=lemma,
                lemma_reading=lemma_reading,
            )
        )

    # Any trailing characters MeCab dropped (e.g. trailing spaces).
    if cursor < len(line):
        words.append(Word(surface=line[cursor:], contains_kanji=False))

    return words
