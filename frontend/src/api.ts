import { AuditResponse } from "./types";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

/**
 * Submits a URL to the backend audit service and returns the parsed audit report.
 *
 * Non-2xx HTTP responses are not treated as errors here — the backend always
 * returns a valid `AuditResponse` shape (with the `error` field populated on
 * failure), so the JSON body is parsed and returned regardless of HTTP status.
 *
 * @param url - The fully-qualified URL to audit (e.g. "https://example.com").
 * @returns A promise that resolves to an `AuditResponse` object.
 * @throws {Error} When the network request itself fails (offline, CORS, etc.).
 */
export async function auditUrl(url: string): Promise<AuditResponse> {
  let response: Response;

  try {
    response = await fetch(`${API_BASE_URL}/api/audit`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ url }),
    });
  } catch {
    throw new Error(
      "Network error — could not reach the audit service. Please try again."
    );
  }

  return response.json() as Promise<AuditResponse>;
}
