/**
 * Request payload sent to the backend audit endpoint.
 */
export interface AuditRequest {
  url: string;
}

/**
 * Response returned by the backend after auditing a URL.
 * All fields except `url` may be null when an error occurs during fetching or parsing.
 */
export interface AuditResponse {
  url: string;
  status_code: number | null;
  response_time_ms: number | null;
  title: string | null;
  meta_description: string | null;
  h1_count: number | null;
  images_missing_alt: number | null;
  word_count: number | null;
  error: string | null;
  warning: string | null;
}

/**
 * Discriminated union representing the four possible UI phases:
 * idle (initial), loading (request in-flight), success (report ready), or error (request failed).
 */
export type AppState =
  | { phase: "idle" }
  | { phase: "loading" }
  | { phase: "success"; data: AuditResponse }
  | { phase: "error"; message: string };
