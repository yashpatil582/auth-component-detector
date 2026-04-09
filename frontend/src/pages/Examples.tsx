import ExampleGrid from "../components/ExampleGrid";

export default function Examples() {
  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Live Examples</h1>
        <p className="text-gray-600">
          Authentication components scraped in real-time from 5 different websites,
          including news, e-commerce, SaaS, banking, and testing platforms.
        </p>
      </div>
      <ExampleGrid />
    </div>
  );
}
