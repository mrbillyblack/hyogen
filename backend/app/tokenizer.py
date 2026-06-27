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
    for node in _tagger(line):
        surface = node.surface
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

        words.append(
            Word(
                surface=surface,
                reading=reading,
                pos=pos,
                contains_kanji=contains,
                kanji=kanji_chars,
            )
        )
    return words
