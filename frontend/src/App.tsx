import { useState } from "react";
import { SearchBar } from "./components/SearchBar";
import { LyricsPane } from "./components/LyricsPane";
import { GlossaryPane } from "./components/GlossaryPane";
import { Menu } from "./components/Menu";
import { analyzeSong, searchSongs } from "./api";
import { useTheme } from "./useTheme";
import type { AnalyzeResponse, SearchResult } from "./types";

function looksLikeLink(text: string): boolean {
  return (
    /youtu\.?be|youtube\.com|music\.youtube/.test(text) ||
    /^https?:\/\//.test(text)
  );
}

export default function App() {
  const { theme, setTheme } = useTheme();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<SearchResult[] | null>(null);
  const [analysis, setAnalysis] = useState<AnalyzeResponse | null>(null);

  async function analyze(input: { videoId?: string; url?: string }) {
    setError(null);
    setResults(null);
    setLoading(true);
    try {
      const data = await analyzeSong(input);
      setAnalysis(data);
      if (!data.has_lyrics) setError("No lyrics found for this song.");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmit(text: string) {
    if (looksLikeLink(text)) {
      await analyze({ url: text });
      return;
    }
    setError(null);
    setResults(null);
    setLoading(true);
    try {
      const hits = await searchSongs(text);
      setResults(hits);
      if (hits.length === 0) setError("No songs found.");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Search failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>
          hyōgen <span className="app-kanji">表現</span>
        </h1>
        <Menu theme={theme} setTheme={setTheme} />
      </header>

      <div className="search-area">
        <SearchBar onSubmit={handleSubmit} loading={loading} />

        <p className="demo-note">
          Demo — lyrics come from YouTube Music and aren&rsquo;t available for
          every song, so some links won&rsquo;t return results.
        </p>

        {error && <p className="error">{error}</p>}

        {results && results.length > 0 && (
          <ul className="results">
            {results.map((r) => (
              <li key={r.videoId}>
                <button type="button" onClick={() => analyze({ videoId: r.videoId })}>
                  <span className="result-title">{r.title ?? r.videoId}</span>
                  <span className="result-meta">
                    {[r.artist, r.album, r.duration].filter(Boolean).join(" · ")}
                  </span>
                </button>
              </li>
            ))}
          </ul>
        )}

        {analysis?.has_lyrics && analysis.title && (
          <p className="now-playing">{analysis.title}</p>
        )}
      </div>

      <main className="panes">
        <LyricsPane lines={analysis?.lines ?? []} />
        <GlossaryPane
          words={analysis?.word_glossary ?? []}
          kanji={analysis?.glossary ?? {}}
        />
      </main>
    </div>
  );
}
