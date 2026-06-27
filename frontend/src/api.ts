import type { AnalyzeResponse, SearchResult, WordEntry } from "./types";

const BASE = "/api";

async function handle<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      if (body?.detail) detail = body.detail;
    } catch {
      // non-JSON error body; keep statusText
    }
    throw new Error(detail);
  }
  return res.json() as Promise<T>;
}

export async function searchSongs(q: string): Promise<SearchResult[]> {
  const res = await fetch(`${BASE}/search?q=${encodeURIComponent(q)}`);
  return handle<SearchResult[]>(res);
}

export async function analyzeSong(input: {
  videoId?: string;
  url?: string;
}): Promise<AnalyzeResponse> {
  const res = await fetch(`${BASE}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
  return handle<AnalyzeResponse>(res);
}

export async function exportAnkiDeck(
  title: string | null,
  words: WordEntry[],
): Promise<Blob> {
  const res = await fetch(`${BASE}/anki`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, words }),
  });
  if (!res.ok) throw new Error("Anki export failed");
  return res.blob();
}
