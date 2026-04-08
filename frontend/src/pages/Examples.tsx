import ExampleGrid from "../components/ExampleGrid";

export default function Examples() {
  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Pre-Scraped Examples</h1>
        <p className="text-gray-600">
          Authentication components detected from 5 different websites, including both
          server-rendered and JavaScript-rendered pages.
        </p>
      </div>
      <ExampleGrid />
    </div>
  );
}
