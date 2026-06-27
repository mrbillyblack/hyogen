"""Lazy, Postgres-backed cache over kanjiapi.dev.

On a cache miss we fetch a single character from kanjiapi.dev, persist it, and
return it. 404s are persisted as `not_found` rows so we never re-fetch a
character kanjiapi has no data for.
"""

import httpx
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .kana import katakana_to_hiragana
from .models import Kanji
from .schemas import KanjiInfo

# kanjiapi.dev rejects the default httpx User-Agent with a 403.
_HEADERS = {"User-Agent": "hyogen/0.1 (+https://github.com/; kanjiapi.dev client)"}


def _to_info(row: Kanji) -> KanjiInfo:
    if row.not_found:
        return KanjiInfo(character=row.character, found=False)

    kun = row.kun_readings or []
    on = row.on_readings or []
    # Build a deduped hiragana reading list: kun readings as-is, on readings
    # converted from katakana. Strip okurigana markers (e.g. "やま.し").
    seen: set[str] = set()
    readings_hiragana: list[str] = []
    for r in [*kun, *(katakana_to_hiragana(o) for o in on)]:
        clean = r.replace(".", "").replace("-", "").replace("ー", "")
        if clean and clean not in seen:
            seen.add(clean)
            readings_hiragana.append(clean)

    return KanjiInfo(
        character=row.character,
        found=True,
        readings_hiragana=readings_hiragana,
        kun_readings=kun,
        on_readings=on,
        meanings=row.meanings or [],
        grade=row.grade,
        jlpt=row.jlpt,
        stroke_count=row.stroke_count,
    )


async def _persist(session: AsyncSession, values: dict) -> None:
    """Upsert a kanji row, ignoring races between concurrent requests."""
    stmt = insert(Kanji).values(**values)
    stmt = stmt.on_conflict_do_update(
        index_elements=[Kanji.character],
        set_={k: v for k, v in values.items() if k != "character"},
    )
    await session.execute(stmt)
    await session.commit()


async def _fetch_from_api(client: httpx.AsyncClient, char: str) -> dict | None:
    """Return the kanjiapi payload, or None if the character is unknown (404)."""
    resp = await client.get(f"{settings.kanjiapi_base}/kanji/{char}")
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    return resp.json()


async def get_many(session: AsyncSession, chars: list[str]) -> dict[str, KanjiInfo]:
    """Resolve a set of kanji characters, fetching only cache misses.

    `chars` should already be deduplicated kanji. Returns a mapping keyed by
    character.
    """
    if not chars:
        return {}

    unique = list(dict.fromkeys(chars))
    result: dict[str, KanjiInfo] = {}

    # 1) Load whatever is already cached.
    cached = (
        await session.execute(select(Kanji).where(Kanji.character.in_(unique)))
    ).scalars().all()
    by_char = {row.character: row for row in cached}
    for ch in unique:
        if ch in by_char:
            result[ch] = _to_info(by_char[ch])

    # 2) Fetch the misses from kanjiapi.dev.
    misses = [ch for ch in unique if ch not in by_char]
    if misses:
        async with httpx.AsyncClient(
            timeout=settings.http_timeout, headers=_HEADERS
        ) as client:
            for ch in misses:
                try:
                    payload = await _fetch_from_api(client, ch)
                except httpx.HTTPError:
                    # Transient failure: skip caching, surface as "not found"
                    # for this response without poisoning the cache.
                    result[ch] = KanjiInfo(character=ch, found=False)
                    continue

                if payload is None:
                    await _persist(session, {"character": ch, "not_found": True})
                    result[ch] = KanjiInfo(character=ch, found=False)
                    continue

                values = {
                    "character": ch,
                    "not_found": False,
                    "grade": payload.get("grade"),
                    "jlpt": payload.get("jlpt"),
                    "stroke_count": payload.get("stroke_count"),
                    "unicode": payload.get("unicode"),
                    "heisig_en": payload.get("heisig_en"),
                    "meanings": payload.get("meanings") or [],
                    "kun_readings": payload.get("kun_readings") or [],
                    "on_readings": payload.get("on_readings") or [],
                    "name_readings": payload.get("name_readings") or [],
                    "raw": payload,
                }
                await _persist(session, values)
                # Build the info from a transient row (avoids a re-select).
                result[ch] = _to_info(Kanji(**values))

    return result


async def get_one(session: AsyncSession, char: str) -> KanjiInfo:
    return (await get_many(session, [char]))[char]
