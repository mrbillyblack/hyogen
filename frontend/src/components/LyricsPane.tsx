import { Pane } from "./Pane";
import type { Line } from "../types";

interface Props {
  lines: Line[];
}

/** Lyrics with furigana: kanji-bearing words render the contextual reading. */
export function LyricsPane({ lines }: Props) {
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
              {line.words.map((w, j) =>
                w.reading ? (
                  <ruby key={j}>
                    {w.surface}
                    <rt>{w.reading}</rt>
                  </ruby>
                ) : (
                  <span key={j}>{w.surface}</span>
                ),
              )}
            </p>
          ),
        )
      )}
    </Pane>
  );
}
