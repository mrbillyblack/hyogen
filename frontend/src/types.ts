// Mirrors the backend response models (backend/app/schemas.py).

export interface Word {
  surface: string;
  reading: string | null; // hiragana reading; set only when the word has kanji
  pos: string | null;
  contains_kanji: boolean;
  kanji: string[];
  lemma: string | null;
  lemma_reading: string | null;
}

export interface Line {
  text: string;
  words: Word[];
}

export interface WordEntry {
  word: string;
  reading: string | null;
  definitions: string[];
  kanji: string[];
}

export interface KanjiInfo {
  character: string;
  found: boolean;
  readings_hiragana: string[];
  kun_readings: string[];
  on_readings: string[];
  meanings: string[];
  grade: number | null;
  jlpt: number | null;
  stroke_count: number | null;
}

export interface AnalyzeResponse {
  video_id: string;
  title: string | null;
  source: string | null;
  has_lyrics: boolean;
  lines: Line[];
  word_glossary: WordEntry[];
  glossary: Record<string, KanjiInfo>;
}

export interface SearchResult {
  videoId: string;
  title: string | null;
  artist: string | null;
  album: string | null;
  duration: string | null;
}
