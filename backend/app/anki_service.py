"""Build an Anki deck (.apkg) from the word glossary.

Front = the kanji word; back = its kana reading + English definition.
"""

import os
import tempfile
import zlib

import genanki

from .schemas import WordEntry

# Stable model id so re-imports update the same note type rather than duplicating.
_MODEL_ID = 1607392319

_MODEL = genanki.Model(
    _MODEL_ID,
    "Hyogen Word",
    fields=[{"name": "Kanji"}, {"name": "Reading"}, {"name": "Meaning"}],
    templates=[
        {
            "name": "Kanji → Reading + Meaning",
            "qfmt": '<div class="kanji">{{Kanji}}</div>',
            "afmt": '{{FrontSide}}<hr id="answer">'
            '<div class="reading">{{Reading}}</div>'
            '<div class="meaning">{{Meaning}}</div>',
        }
    ],
    css=(
        ".card{font-family:sans-serif;text-align:center;color:#1f2330;"
        "background:#fff}"
        ".kanji{font-size:48px;font-weight:700}"
        ".reading{font-size:24px;color:#4f46e5;margin-top:12px}"
        ".meaning{font-size:20px;margin-top:8px}"
    ),
)


def _deck_id(name: str) -> int:
    # Derive a stable deck id from the name so the same song maps to one deck.
    return 1_500_000_000 + (zlib.crc32(name.encode("utf-8")) % 100_000_000)


def build_deck(title: str | None, words: list[WordEntry]) -> bytes:
    name = f"Hyogen — {title}" if title else "Hyogen — Lyrics"
    deck = genanki.Deck(_deck_id(name), name)

    for w in words:
        reading = w.reading or ""
        meaning = "; ".join(w.definitions)
        if not meaning:
            continue
        deck.add_note(
            genanki.Note(model=_MODEL, fields=[w.word, reading, meaning])
        )

    # genanki writes to a path; round-trip through a temp file to get bytes.
    tmp = tempfile.NamedTemporaryFile(suffix=".apkg", delete=False)
    try:
        tmp.close()
        genanki.Package(deck).write_to_file(tmp.name)
        with open(tmp.name, "rb") as f:
            return f.read()
    finally:
        os.unlink(tmp.name)
