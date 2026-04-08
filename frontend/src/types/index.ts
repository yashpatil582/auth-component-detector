export interface AuthComponent {
  component_type: string;
  html_snippet: string;
  selector: string;
  confidence: number;
  attributes: Record<string, string>;
}

export interface ScrapeResponse {
  url: string;
  title: string | null;
  scraped_at: string;
  rendering_method: string;
  auth_components: AuthComponent[];
  full_page_has_auth: boolean;
  detection_summary: string;
  scrape_duration_ms: number;
}

export interface ScrapeRequest {
  url: string;
  use_js_rendering: boolean;
  timeout: number;
}
