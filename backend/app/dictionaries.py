"""Shared offline dictionaries, backed by jamdict.

jamdict bundles three datasets in `jamdict-data` (already in the image):
  - JMdict    — Japanese→English words      (used by word_service)
  - KanjiDic2 — per-kanji readings/meanings  (used by kanji_service)
  - JMnedict  — names (unused)

jamdict wraps SQLite, whose connections are thread-affine, so all lookups run
synchronously on the event-loop thread (see kanji_service / word_service) —
never via the thread pool. Lookups are local and sub-millisecond, so this
doesn't meaningfully block the loop, and it means the backend needs no database
server at all.
"""

from jamdict import Jamdict

jam = Jamdict()
