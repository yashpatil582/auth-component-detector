import type { AuthComponent } from "../types";
import CodeBlock from "./CodeBlock";

interface Props {
  component: AuthComponent;
}

const TYPE_LABELS: Record<string, { label: string; color: string }> = {
  login_form: { label: "Login Form", color: "bg-emerald-100 text-emerald-800" },
  oauth_button: { label: "OAuth / SSO", color: "bg-blue-100 text-blue-800" },
  forgot_password_link: { label: "Forgot Password", color: "bg-amber-100 text-amber-800" },
  password_field: { label: "Password Field", color: "bg-red-100 text-red-800" },
  username_field: { label: "Username Field", color: "bg-purple-100 text-purple-800" },
};

function confidenceColor(confidence: number): string {
  if (confidence >= 0.8) return "bg-emerald-500";
  if (confidence >= 0.6) return "bg-yellow-500";
  return "bg-orange-500";
}

export default function ResultCard({ component }: Props) {
  const typeInfo = TYPE_LABELS[component.component_type] || {
    label: component.component_type,
    color: "bg-gray-100 text-gray-800",
  };

  return (
    <div className="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm">
      <div className="px-4 py-3 border-b border-gray-100 flex items-center justify-between flex-wrap gap-2">
        <div className="flex items-center gap-2">
          <span className={`px-2.5 py-0.5 text-xs font-medium rounded-full ${typeInfo.color}`}>
            {typeInfo.label}
          </span>
          <code className="text-xs text-gray-500 bg-gray-50 px-2 py-0.5 rounded">
            {component.selector}
          </code>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-500">Confidence</span>
          <div className="w-20 h-2 bg-gray-200 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-700 ${confidenceColor(component.confidence)}`}
              style={{ width: `${component.confidence * 100}%` }}
            />
          </div>
          <span className="text-xs font-medium text-gray-700">
            {(component.confidence * 100).toFixed(0)}%
          </span>
        </div>
      </div>

      <div className="p-4">
        <CodeBlock code={component.html_snippet} />
      </div>

      {Object.keys(component.attributes).length > 0 && (
        <div className="px-4 pb-3">
          <div className="flex flex-wrap gap-1.5">
            {Object.entries(component.attributes).map(([key, value]) => (
              <span
                key={key}
                className="text-xs bg-gray-50 text-gray-600 px-2 py-0.5 rounded border border-gray-100"
              >
                {key}="{value}"
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
