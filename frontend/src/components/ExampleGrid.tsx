import { useEffect, useState } from "react";
import type { ScrapeResponse } from "../types";
import { getExamples } from "../api/client";
import ResultCard from "./ResultCard";
import LoadingSpinner from "./LoadingSpinner";
import ErrorAlert from "./ErrorAlert";

export default function ExampleGrid() {
  const [examples, setExamples] = useState<ScrapeResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [expandedIdx, setExpandedIdx] = useState<number | null>(null);

  useEffect(() => {
    getExamples()
      .then(setExamples)
      .catch((err) => setError(err.response?.data?.detail || err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading)
    return (
      <div className="flex flex-col items-center justify-center py-12 gap-3">
        <div className="w-10 h-10 border-4 border-gray-200 border-t-emerald-500 rounded-full animate-spin" />
        <p className="text-sm text-gray-500">Scraping 5 demo sites live...</p>
      </div>
    );
  if (error) return <ErrorAlert message={error} />;
  if (examples.length === 0)
    return <p className="text-gray-500 text-sm py-8">No pre-scraped examples available.</p>;

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {examples.map((ex, idx) => (
        <div
          key={ex.url}
          className={`bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm transition hover:shadow-md ${
            expandedIdx === idx ? "sm:col-span-2 lg:col-span-3" : ""
          }`}
        >
          <div className="p-4">
            <div className="flex items-start justify-between gap-2 mb-2">
              <h3 className="font-semibold text-gray-900 text-sm">{ex.title || ex.url}</h3>
              <span
                className={`text-xs px-2 py-0.5 rounded-full shrink-0 ${
                  ex.rendering_method === "javascript"
                    ? "bg-purple-100 text-purple-700"
                    : "bg-gray-100 text-gray-600"
                }`}
              >
                {ex.rendering_method === "javascript" ? "JS Rendered" : "Static"}
              </span>
            </div>
            <p className="text-xs text-gray-500 mb-2 truncate">{ex.url}</p>
            <p className="text-sm text-gray-700 mb-3">{ex.detection_summary}</p>
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-400">{ex.scrape_duration_ms}ms</span>
              <button
                onClick={() => setExpandedIdx(expandedIdx === idx ? null : idx)}
                className="text-xs text-emerald-600 hover:text-emerald-700 font-medium"
              >
                {expandedIdx === idx ? "Collapse" : `View ${ex.auth_components.length} component(s)`}
              </button>
            </div>
          </div>

          {expandedIdx === idx && (
            <div className="border-t border-gray-100 p-4 space-y-3 bg-gray-50">
              {ex.auth_components.map((comp, cIdx) => (
                <ResultCard key={cIdx} component={comp} />
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
