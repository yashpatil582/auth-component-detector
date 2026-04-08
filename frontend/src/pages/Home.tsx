import { useState } from "react";
import type { ScrapeResponse } from "../types";
import { scrapeUrl } from "../api/client";
import UrlInput from "../components/UrlInput";
import ResultCard from "../components/ResultCard";
import LoadingSpinner from "../components/LoadingSpinner";
import ErrorAlert from "../components/ErrorAlert";

export default function Home() {
  const [result, setResult] = useState<ScrapeResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleScan = async (url: string, useJs: boolean) => {
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const data = await scrapeUrl({
        url,
        use_js_rendering: useJs,
        timeout: useJs ? 25 : 15,
      });
      setResult(data);
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } }; message?: string };
      setError(axiosErr.response?.data?.detail || axiosErr.message || "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Auth Component Scanner</h1>
        <p className="text-gray-600">
          Enter a URL to detect login forms, password fields, OAuth buttons, and other
          authentication components.
        </p>
      </div>

      <UrlInput onSubmit={handleScan} isLoading={loading} />

      <div className="mt-8">
        {loading && <LoadingSpinner />}

        {error && (
          <ErrorAlert message={error} onDismiss={() => setError("")} />
        )}

        {result && !loading && (
          <div className="space-y-4">
            <div className="flex items-center justify-between flex-wrap gap-2 pb-2 border-b border-gray-200">
              <div>
                <h2 className="text-lg font-semibold text-gray-900">
                  {result.title || result.url}
                </h2>
                <p className="text-sm text-gray-500">{result.detection_summary}</p>
              </div>
              <div className="flex gap-2 text-xs">
                <span className="bg-gray-100 text-gray-600 px-2 py-1 rounded">
                  {result.rendering_method}
                </span>
                <span className="bg-gray-100 text-gray-600 px-2 py-1 rounded">
                  {result.scrape_duration_ms}ms
                </span>
              </div>
            </div>

            {result.auth_components.length === 0 ? (
              <div className="text-center py-8">
                <svg className="w-12 h-12 text-gray-300 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.75 9.75l4.5 4.5m0-4.5l-4.5 4.5M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p className="text-gray-500">No authentication components found on this page.</p>
                <p className="text-gray-400 text-sm mt-1">
                  Try enabling JavaScript rendering for SPAs, or check a different URL.
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                {result.auth_components.map((comp, idx) => (
                  <ResultCard key={idx} component={comp} />
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
