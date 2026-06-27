import { Pane } from "./Pane";
import type { Line, Word } from "../types";

interface Props {
  lines: Line[];
  glossaryWords: Set<string>;
  activeWord: string | null;
  onActivate: (word: string) => void;
}

function ruby(w: Word) {
  return w.reading ? (
    <ruby>
      {w.surface}
      <rt>{w.reading}</rt>
    </ruby>
  ) : (
    w.surface
  );
}

/**
 * Lyrics with furigana. Kanji words that have a glossary entry are interactive:
 * hovering or tapping one activates the matching glossary word on the right.
 */
export function LyricsPane({ lines, glossaryWords, activeWord, onActivate }: Props) {
  return (
    <Pane title="Lyrics">
      {lines.length === 0 ? (
        <p className="empty">Paste a link or search a song to see lyrics.</p>
      ) : (
        lines.map((line, i) =>
          line.text.trim() === "" ? (
            <div key={i} className="lyric-blank" />
          ) : (
            <p key={i} className="lyric-line">
              {line.words.map((w, j) => {
                const key = w.lemma || w.surface;
                const linkable = w.contains_kanji && glossaryWords.has(key);
                if (!linkable) {
                  return (
                    <span key={j} className="lyric-plain">
                      {ruby(w)}
                    </span>
                  );
                }
                return (
                  <span
                    key={j}
                    className={
                      "lyric-word" + (activeWord === key ? " active" : "")
                    }
                    title="Show in glossary"
                    onMouseEnter={() => onActivate(key)}
                    onClick={() => onActivate(key)}
                  >
                    {ruby(w)}
                  </span>
                );
              })}
            </p>
          ),
        )
      )}
    </Pane>
  );
}
