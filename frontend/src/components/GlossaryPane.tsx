import { useEffect, useRef } from "react";
import { Pane } from "./Pane";
import type { KanjiInfo, WordEntry } from "../types";

interface Props {
  words: WordEntry[];
  kanji: Record<string, KanjiInfo>;
  activeWord: string | null;
  loading: boolean;
}

/**
 * Word-level glossary. Each entry shows the word, reading and definition, and
 * expands to its per-kanji breakdown. When a lyric word is hovered/tapped, the
 * matching entry highlights and scrolls into view.
 */
export function GlossaryPane({ words, kanji, activeWord, loading }: Props) {
  const refs = useRef(new Map<string, HTMLDetailsElement>());

  useEffect(() => {
    if (!activeWord) return;
    refs.current.get(activeWord)?.scrollIntoView({
      block: "nearest",
      behavior: "smooth",
    });
  }, [activeWord]);

  return (
    <Pane title="Glossary">
      {loading ? (
        <p className="loading">Loading…</p>
      ) : words.length === 0 ? (
        <p className="empty">Word definitions will appear here.</p>
      ) : (
        words.map((w) => {
          const breakdown = w.kanji
            .map((ch) => kanji[ch])
            .filter((k): k is KanjiInfo => !!k && k.found);

          return (
            <details
              key={w.word}
              ref={(el) => {
                if (el) refs.current.set(w.word, el);
                else refs.current.delete(w.word);
              }}
              className={"g-word" + (activeWord === w.word ? " active" : "")}
            >
              <summary>
                <span className="g-kanji">{w.word}</span>
                {w.reading && <span className="g-reading">{w.reading}</span>}
                <span className="g-dash">—</span>
                <span className="g-meaning">
                  {w.definitions.length > 0
                    ? w.definitions.slice(0, 3).join("; ")
                    : "(no definition found)"}
                </span>
              </summary>

              {breakdown.length > 0 && (
                <div className="g-breakdown">
                  {breakdown.map((k) => (
                    <div key={k.character} className="g-kanji-row">
                      <span className="g-kanji-char">{k.character}</span>
                      <span className="g-kanji-reading">
                        {k.readings_hiragana.slice(0, 3).join("・")}
                      </span>
                      <span className="g-kanji-meaning">
                        {k.meanings.slice(0, 3).join(", ")}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </details>
          );
        })
      )}
    </Pane>
  );
}
