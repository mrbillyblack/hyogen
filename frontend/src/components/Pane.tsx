import { type ReactNode, useRef } from "react";

interface Props {
  title: string;
  children: ReactNode;
}

/** A titled, scrollable container with up/down scroll arrows (per the sketch). */
export function Pane({ title, children }: Props) {
  const bodyRef = useRef<HTMLDivElement>(null);

  function scroll(direction: 1 | -1) {
    bodyRef.current?.scrollBy({ top: direction * 220, behavior: "smooth" });
  }

  return (
    <section className="pane">
      <h2 className="pane-title">{title}</h2>
      <div className="pane-inner">
        <div className="pane-body" ref={bodyRef}>
          {children}
        </div>
        <div className="pane-scroll">
          <button
            type="button"
            aria-label={`Scroll ${title} up`}
            onClick={() => scroll(-1)}
          >
            ▲
          </button>
          <button
            type="button"
            aria-label={`Scroll ${title} down`}
            onClick={() => scroll(1)}
          >
            ▼
          </button>
        </div>
      </div>
    </section>
  );
}
