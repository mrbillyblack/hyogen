"""Character classification and kana conversion.

The core idea (per the project brief): rather than searching for kanji directly,
we walk the text and pick out whatever is *not* hiragana and *not* katakana.
Anything in the CJK ideograph range is treated as a kanji worth annotating.
"""

# Unicode blocks
_HIRAGANA = (0x3040, 0x309F)
_KATAKANA = (0x30A0, 0x30FF)  # incl. the small-kana and the long-vowel mark ー
_KATAKANA_PHONETIC_EXT = (0x31F0, 0x31FF)
# CJK Unified Ideographs (main block) + common extension A.
_CJK = (0x4E00, 0x9FFF)
_CJK_EXT_A = (0x3400, 0x4DBF)
_KANJI_ITERATION_MARK = 0x3005  # 々 (repeats the previous kanji)


def _in(cp: int, block: tuple[int, int]) -> bool:
    return block[0] <= cp <= block[1]


def is_hiragana(ch: str) -> bool:
    return _in(ord(ch), _HIRAGANA)


def is_katakana(ch: str) -> bool:
    cp = ord(ch)
    return _in(cp, _KATAKANA) or _in(cp, _KATAKANA_PHONETIC_EXT)


def is_kanji(ch: str) -> bool:
    cp = ord(ch)
    return _in(cp, _CJK) or _in(cp, _CJK_EXT_A) or cp == _KANJI_ITERATION_MARK


def classify(ch: str) -> str:
    """Return one of: 'hiragana', 'katakana', 'kanji', 'other'."""
    if is_hiragana(ch):
        return "hiragana"
    if is_katakana(ch):
        return "katakana"
    if is_kanji(ch):
        return "kanji"
    return "other"


def katakana_to_hiragana(text: str) -> str:
    """Convert katakana to hiragana, leaving everything else untouched.

    Used so on'yomi readings (which kanjiapi returns in katakana) can be shown
    in hiragana alongside the kun'yomi readings.
    """
    out: list[str] = []
    for ch in text:
        cp = ord(ch)
        # Convert the gojuon range only; keep the long-vowel mark ー and the
        # middle dot ・ as-is.
        if 0x30A1 <= cp <= 0x30F6:
            out.append(chr(cp - 0x60))
        else:
            out.append(ch)
    return "".join(out)
