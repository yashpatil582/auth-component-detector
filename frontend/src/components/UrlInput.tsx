import { useState } from "react";

interface Props {
  onSubmit: (url: string, useJs: boolean) => void;
  isLoading: boolean;
}

export default function UrlInput({ onSubmit, isLoading }: Props) {
  const [url, setUrl] = useState("");
  const [useJs, setUseJs] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;
    let finalUrl = url.trim();
    if (!finalUrl.startsWith("http")) {
      finalUrl = "https://" + finalUrl;
    }
    onSubmit(finalUrl, useJs);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <div className="flex gap-2">
        <input
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://example.com/login"
          className="flex-1 px-4 py-3 bg-white border border-gray-300 rounded-lg text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent text-sm"
          disabled={isLoading}
        />
        <button
          type="submit"
          disabled={isLoading || !url.trim()}
          className="px-6 py-3 bg-emerald-600 text-white font-medium rounded-lg hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed transition text-sm whitespace-nowrap"
        >
          {isLoading ? "Scanning..." : "Scan"}
        </button>
      </div>

      <label className="flex items-center gap-2 text-sm text-gray-600 cursor-pointer select-none">
        <input
          type="checkbox"
          checked={useJs}
          onChange={(e) => setUseJs(e.target.checked)}
          className="w-4 h-4 text-emerald-600 rounded border-gray-300 focus:ring-emerald-500"
          disabled={isLoading}
        />
        <span>Enable JavaScript rendering</span>
        <span className="text-gray-400 text-xs" title="Use for SPAs (React, Angular, Vue) where the login form loads via JavaScript. Slower but more thorough.">
          (for SPAs — slower)
        </span>
      </label>
    </form>
  );
}
