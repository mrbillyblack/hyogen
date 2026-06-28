# Hyogen 表現

Annotate Japanese song lyrics. Hyogen fetches lyrics from YouTube Music,
segments each line into words, spells the kanji-bearing words out in hiragana
(contextual furigana via MeCab), and defines each **word** in English (JMdict) —
with a per-kanji breakdown available underneath.

## How it works

1. **Lyrics** — given a YouTube/YT Music `videoId` (or URL), the backend uses a
   vendored fork of [`ytmusicapi`](./ytmusicapi) to resolve the song's lyrics
   browseId and fetch the lyric text. No auth required for public lyrics.
2. **Tokenization** — each line is segmented into words with MeCab
   (fugashi + unidic-lite). A word's reading comes from UniDic's `kana` field
   (the kana spelling, e.g. 東京 → トウキョウ — not the phonetic `pron`,
   トーキョー), folded to hiragana. This gives the reading actually used in
   context (回る → まわる), which a per-character lookup cannot.
3. **Word definitions** — each kanji-bearing word's dictionary form (lemma) is
   looked up in **JMdict** via `jamdict` (offline). The JMdict sense whose kana
   matches MeCab's contextual reading is chosen, so 回る resolves to "to turn"
   (まわる), not "to go around" (めぐる). This is the primary glossary —
   defining 表現 ("expression"), not just 表 and 現.
4. **Per-kanji meanings** — every unique kanji (anything *not* hiragana/katakana
   in the CJK range, plus the 々 iteration mark) is looked up in **KanjiDic2**
   (bundled with `jamdict`, the same dataset kanjiapi.dev is built from). These
   power the collapsible per-kanji breakdown shown under each glossary word.
5. **No database** — both dictionaries (JMdict, KanjiDic2) and the MeCab
   dictionary ship inside the image, so the backend is fully self-contained:
   no Postgres, no kanjiapi.dev calls, no network at lookup time. The only
   runtime network call is fetching lyrics from YouTube Music. This makes it
   ideal for stateless, scale-to-zero hosting (e.g. Cloud Run).

## Stack

- **React + Vite** (`frontend/`) — installable PWA; search/paste box, a Lyrics
  pane (furigana) and a word Glossary pane, light/dark theme, hamburger menu
- **FastAPI** (`backend/app`) — async API, no database
- **MeCab** (fugashi + unidic-lite) — word segmentation + contextual readings
- **jamdict + jamdict-data** — offline JMdict (words) + KanjiDic2 (kanji)
- **genanki** — exports the glossary as an Anki deck (.apkg)
- **Caddy** — reverse proxy on `:80` (auto-TLS in production)
- **ytmusicapi fork** (`ytmusicapi/`) — vendored, installed from source

## Project structure

```
hyogen/
├── ytmusicapi/             # vendored fork (lyrics source)
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app + routes
│   │   ├── config.py          # env-driven settings (CORS)
│   │   ├── schemas.py         # Pydantic request/response models
│   │   ├── kana.py            # char classification + katakana→hiragana
│   │   ├── tokenizer.py       # MeCab word segmentation + contextual readings
│   │   ├── dictionaries.py    # shared jamdict instance (JMdict + KanjiDic2)
│   │   ├── kanji_service.py   # per-kanji readings/meanings from KanjiDic2
│   │   ├── word_service.py    # JMdict (jamdict) word definitions
│   │   ├── anki_service.py    # builds an Anki deck (.apkg) from the glossary
│   │   ├── lyrics_service.py  # ytmusicapi wrapper (search + videoId/URL → lyrics)
│   │   └── analyze.py         # ties lyrics + tokenizer + kanji/word lookups
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                # React + Vite PWA
│   ├── src/
│   │   ├── App.tsx             # search + Lyrics/Glossary panes + menu
│   │   ├── api.ts              # fetch wrappers (/api/*)
│   │   ├── types.ts           # mirrors backend response models
│   │   ├── useTheme.ts         # light/dark theme (persisted)
│   │   └── components/         # SearchBar, Pane, LyricsPane, GlossaryPane, Menu
│   ├── vite.config.ts         # dev proxy to backend + PWA manifest
│   └── package.json
├── docker-compose.yml       # api + frontend + caddy (no database)
├── Caddyfile
└── .env.example
```

## Running

```bash
docker compose up -d --build
```

Brings up the API, the frontend dev server, and Caddy (no database):

- **Frontend** — http://localhost:5173 (Vite dev server, hot reload)
- **API** — http://localhost (through Caddy), docs at http://localhost/docs

The frontend container proxies `/api/*` to the backend (`VITE_API_PROXY`), so
the UI calls same-origin paths and there's no CORS to manage in dev.

### Frontend (production / Cloudflare Pages)

The frontend is a static SPA. Build with `npm run build` (output in
`frontend/dist`) and deploy `dist/` to Cloudflare Pages. In production, point the
app at the API origin (e.g. via a Pages rewrite of `/api/*`, or a build-time
base URL).

To run the API directly (no database needed — all data is bundled):

```bash
cd backend
pip install -r requirements.txt
pip install ../ytmusicapi
uvicorn app.main:app --reload --port 8000
```

## API

| Method | Path | Description |
|---|---|---|
| GET  | `/health` | Liveness check |
| GET  | `/api/search?q=` | Search YouTube Music for songs (returns videoIds) |
| POST | `/api/analyze` | Annotate a song's lyrics. Body: `{"videoId": "..."}` or `{"url": "..."}` |
| POST | `/api/anki` | Build an Anki deck (.apkg) from the glossary. Body: `{"title", "words": [...]}` |
| GET  | `/api/kanji/{char}` | Readings + meanings for a single kanji |

Interactive docs at `http://localhost/docs`.

### Example

```bash
curl -X POST http://localhost/api/analyze \
  -H 'Content-Type: application/json' \
  -d '{"videoId":"Gzuk7oK7ngE"}'
```

```jsonc
{
  "video_id": "Gzuk7oK7ngE",
  "title": "反面教師 - Bad example",
  "has_lyrics": true,
  "lines": [
    {
      "text": "罵られたって ウザイ日だって",
      "words": [
        {"surface": "罵ら", "reading": "ののしら", "lemma": "罵る",
         "contains_kanji": true, "kanji": ["罵"]}
        // ...one entry per word; `reading` is the contextual furigana
      ]
    }
  ],
  "word_glossary": [
    {"word": "罵る", "reading": "ののしる",
     "definitions": ["to abuse (verbally)", "to curse at"], "kanji": ["罵"]},
    {"word": "此の世", "reading": "このよ",
     "definitions": ["this world", "world of the living"], "kanji": ["世"]}
    // ...one entry per unique word (dictionary form), in order of appearance
  ],
  "glossary": {
    "罵": {"character": "罵", "found": true,
           "readings_hiragana": ["ののしる", "ば"], "meanings": ["abuse", "insult"],
           "grade": null, "jlpt": 1, "stroke_count": 15}
    // ...one entry per unique kanji — powers the per-word collapsible breakdown
  }
}
```

`word_glossary` is the primary glossary (whole-word definitions). Each word's
`kanji` are looked up in the per-kanji `glossary` for the expandable breakdown.

## Notes

- Word readings come from MeCab's contextual segmentation, so 回る → まわる and
  今 → いま are resolved correctly, and the matching JMdict sense is chosen. The
  per-kanji `glossary` still lists *all* possible readings per kanji.
- Lyrics come from YouTube Music and aren't available for every song, so some
  links return no lyrics — the UI shows a demo note to that effect.
- **Exports**: "Export PDF" uses the browser's print-to-PDF (a print
  stylesheet hides the UI chrome and flows the lyrics + glossary across pages —
  Japanese renders with system fonts, no font embedding). "Anki deck" downloads
  an `.apkg` (front = kanji word, back = reading + definition) built by
  `genanki`.
- All dictionaries ship as pip wheels (no system packages, no DB): fugashi
  bundles MeCab, unidic-lite the MeCab dictionary, and jamdict-data the JMdict +
  KanjiDic2 SQLite. Together they add ~600 MB to the image but make the backend
  network-free for lookups.
- jamdict's SQLite is thread-affine, so kanji/word lookups run synchronously on
  the event-loop thread (not the thread pool). Lookups are sub-millisecond, so
  this is fine; revisit if you ever need heavy lookup concurrency.
