import { Pane } from "./Pane";
import type { KanjiInfo } from "../types";

interface Props {
  glossary: Record<string, KanjiInfo>;
}

/** One entry per unique kanji: character, hiragana reading(s), English meaning. */
export function GlossaryPane({ glossary }: Props) {
  const entries = Object.values(glossary).filter(
    (k) => k.found && k.meanings.length > 0,
  );

  return (
    <Pane title="Glossary">
      {entries.length === 0 ? (
        <p className="empty">Kanji definitions will appear here.</p>
      ) : (
        entries.map((k) => (
          <div key={k.character} className="glossary-entry">
            <span className="g-kanji">{k.character}</span>
            <span className="g-reading">
              {k.readings_hiragana.slice(0, 2).join("・")}
            </span>
            <span className="g-dash">—</span>
            <span className="g-meaning">{k.meanings.slice(0, 3).join(", ")}</span>
          </div>
        ))
      )}
    </Pane>
  );
}
