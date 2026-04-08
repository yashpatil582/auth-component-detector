import { Link, useLocation } from "react-router-dom";

export default function Header() {
  const location = useLocation();

  return (
    <header className="bg-gray-900 text-white">
      <div className="max-w-5xl mx-auto px-4 py-4 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2 hover:opacity-80 transition">
          <svg
            className="w-7 h-7 text-emerald-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
            />
          </svg>
          <span className="text-lg font-semibold">Auth Detector</span>
        </Link>

        <nav className="flex gap-4">
          <Link
            to="/"
            className={`px-3 py-1.5 rounded-md text-sm font-medium transition ${
              location.pathname === "/"
                ? "bg-gray-700 text-white"
                : "text-gray-300 hover:text-white hover:bg-gray-800"
            }`}
          >
            Scanner
          </Link>
          <Link
            to="/examples"
            className={`px-3 py-1.5 rounded-md text-sm font-medium transition ${
              location.pathname === "/examples"
                ? "bg-gray-700 text-white"
                : "text-gray-300 hover:text-white hover:bg-gray-800"
            }`}
          >
            Examples
          </Link>
        </nav>
      </div>
    </header>
  );
}
