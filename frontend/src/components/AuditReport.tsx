import { AuditResponse } from "../types";

interface AuditReportProps {
  report: AuditResponse;
}

function getStatusCodeStyle(code: number | null): string {
  if (code === null) return "text-gray-500 bg-gray-100";
  if (code >= 200 && code < 300) return "text-green-600 bg-green-100";
  if (code >= 300 && code < 400) return "text-yellow-600 bg-yellow-100";
  return "text-red-600 bg-red-100";
}

interface RowProps {
  label: string;
  children: React.ReactNode;
}

function Row({ label, children }: RowProps) {
  return (
    <div className="flex items-start justify-between py-3 border-b border-gray-100 last:border-b-0">
      <span className="text-sm font-medium text-gray-500 w-44 shrink-0">{label}</span>
      <span className="text-sm text-gray-900 text-right">{children}</span>
    </div>
  );
}

export default function AuditReport({ report }: AuditReportProps) {
  const statusStyle = getStatusCodeStyle(report.status_code);

  return (
    <div className="bg-white rounded-2xl shadow-md p-6 w-full max-w-xl mx-auto">
      <h2 className="text-lg font-semibold text-gray-800 mb-1">Audit Report</h2>
      <p className="text-xs text-gray-400 mb-4 truncate" title={report.url}>
        {report.url}
      </p>

      {report.error && (
        <div className="mb-4 rounded-lg bg-amber-50 border border-amber-200 px-4 py-3 text-sm text-amber-800">
          <span className="font-semibold">Note: </span>
          Some fields could not be retrieved because an error occurred while auditing this page:{" "}
          <span className="italic">{report.error}</span>. Status code and response time are shown
          where available.
        </div>
      )}

      {report.warning && !report.error && (
        <div className="mb-4 rounded-lg bg-yellow-50 border border-yellow-300 px-4 py-3 text-sm text-yellow-800 flex items-start gap-2">
          <span className="mt-0.5 shrink-0" aria-hidden="true">⚠️</span>
          <span>{report.warning}</span>
        </div>
      )}

      <div>
        {/* Status Code */}
        <Row label="Status Code">
          {report.status_code !== null ? (
            <span className={`inline-block px-2 py-0.5 rounded-full text-xs font-semibold ${statusStyle}`}>
              {report.status_code}
            </span>
          ) : (
            <span className="text-gray-400">—</span>
          )}
        </Row>

        {/* Response Time */}
        <Row label="Response Time">
          {report.response_time_ms !== null ? (
            <>{report.response_time_ms.toFixed(0)} ms</>
          ) : (
            <span className="text-gray-400">—</span>
          )}
        </Row>

        {/* Title */}
        <Row label="Title">
          {report.title !== null ? (
            report.title
          ) : (
            <span className="text-gray-400">Not found</span>
          )}
        </Row>

        {/* Meta Description */}
        <Row label="Meta Description">
          {report.meta_description !== null ? (
            report.meta_description
          ) : (
            <span className="text-gray-400">Not set</span>
          )}
        </Row>

        {/* H1 Count */}
        <Row label="H1 Count">
          {report.h1_count !== null ? (
            report.h1_count
          ) : (
            <span className="text-gray-400">—</span>
          )}
        </Row>

        {/* Images Missing Alt */}
        <Row label="Images Missing Alt">
          {report.images_missing_alt !== null ? (
            <span className={report.images_missing_alt > 0 ? "text-red-600 font-medium" : ""}>
              {report.images_missing_alt}
            </span>
          ) : (
            <span className="text-gray-400">—</span>
          )}
        </Row>

        {/* Word Count */}
        <Row label="Word Count">
          {report.word_count !== null ? (
            report.word_count.toLocaleString()
          ) : (
            <span className="text-gray-400">—</span>
          )}
        </Row>
      </div>
    </div>
  );
}
