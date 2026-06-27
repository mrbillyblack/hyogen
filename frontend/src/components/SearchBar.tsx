import { type FormEvent, useState } from "react";

interface Props {
  onSubmit: (text: string) => void;
  loading: boolean;
}

export function SearchBar({ onSubmit, loading }: Props) {
  const [text, setText] = useState("");

  function submit(e: FormEvent) {
    e.preventDefault();
    const t = text.trim();
    if (t) onSubmit(t);
  }

  return (
    <form className="searchbar" onSubmit={submit}>
      <input
        className="searchbar-input"
        type="text"
        placeholder="Paste a link to YT Music, or search a song…"
        value={text}
        onChange={(e) => setText(e.target.value)}
        disabled={loading}
        autoFocus
      />
      <button className="searchbar-btn" type="submit" disabled={loading}>
        {loading ? "…" : "Go"}
      </button>
    </form>
  );
}
