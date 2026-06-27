import { useEffect, useRef, useState } from "react";
import type { Theme } from "../useTheme";

interface Props {
  theme: Theme;
  setTheme: (t: Theme) => void;
}

/** Top-right hamburger menu: a downward flex of "How to use" + theme toggle. */
export function Menu({ theme, setTheme }: Props) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  // Close on outside click or Escape.
  useEffect(() => {
    if (!open) return;
    function onClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") setOpen(false);
    }
    document.addEventListener("mousedown", onClick);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onClick);
      document.removeEventListener("keydown", onKey);
    };
  }, [open]);

  return (
    <div className="menu" ref={ref}>
      <button
        className="menu-button"
        aria-label="Menu"
        aria-expanded={open}
        onClick={() => setOpen((v) => !v)}
      >
        ☰
      </button>

      {open && (
        <div className="menu-panel">
          <section className="menu-section">
            <h3>How to use</h3>
            <ol>
              <li>Paste a YouTube Music link, or type a song name to search.</li>
              <li>Pick a result to load its lyrics.</li>
              <li>
                <strong>Lyrics</strong> show furigana over each word; the{" "}
                <strong>Glossary</strong> defines each word.
              </li>
              <li>Expand a glossary word to see its individual kanji.</li>
              <li>Export the result to PDF or an Anki deck.</li>
            </ol>

            <div className="menu-credit">
              <p>© 2026 Billy Black</p>
              <a
                href="https://ko-fi.com/F8U5224XOY"
                target="_blank"
                rel="noopener noreferrer"
              >
                <img
                  height="36"
                  style={{ border: 0, height: 36 }}
                  src="https://storage.ko-fi.com/cdn/kofi6.png?v=6"
                  alt="Buy Me a Coffee at ko-fi.com"
                />
              </a>
            </div>
          </section>

          <section className="menu-section">
            <h3>Appearance</h3>
            <div className="theme-toggle" role="group" aria-label="Theme">
              <button
                className={theme === "light" ? "active" : ""}
                onClick={() => setTheme("light")}
              >
                ☀ Light
              </button>
              <button
                className={theme === "dark" ? "active" : ""}
                onClick={() => setTheme("dark")}
              >
                ☾ Dark
              </button>
            </div>
          </section>
        </div>
      )}
    </div>
  );
}
