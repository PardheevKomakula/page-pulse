import { useState } from "react";
import { AppState } from "./types";
import { auditUrl } from "./api";
import { AuditForm } from "./components/AuditForm";
import AuditReport from "./components/AuditReport";
import ErrorBlock from "./components/ErrorBlock";
import Footer from "./components/Footer";

export default function App() {
  const [url, setUrl] = useState<string>("");
  const [appState, setAppState] = useState<AppState>({ phase: "idle" });

  async function handleSubmit() {
    if (url.trim() === "") return;

    setAppState({ phase: "loading" });

    try {
      const data = await auditUrl(url.trim());
      setAppState({ phase: "success", data });
    } catch (err) {
      const message =
        err instanceof Error
          ? err.message
          : "An unexpected error occurred. Please try again.";
      setAppState({ phase: "error", message });
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-5">
        <div className="max-w-xl mx-auto">
          <h1 className="text-2xl font-bold text-indigo-600 tracking-tight">
            Page Pulse
          </h1>
          <p className="text-sm text-gray-500 mt-0.5">
            Enter a URL to audit its SEO signals and page health.
          </p>
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1 px-6 py-8">
        <div className="max-w-xl mx-auto flex flex-col gap-6">
          {/* Input form — always visible */}
          <AuditForm
            url={url}
            isLoading={appState.phase === "loading"}
            onChange={setUrl}
            onSubmit={handleSubmit}
          />

          {/* Result area */}
          {appState.phase === "idle" && (
            <p className="text-center text-sm text-gray-400">
              Your audit report will appear here.
            </p>
          )}

          {appState.phase === "success" && (
            <AuditReport report={appState.data} />
          )}

          {appState.phase === "error" && (
            <ErrorBlock message={appState.message} />
          )}
        </div>
      </main>

      {/* Footer — always visible */}
      <Footer />
    </div>
  );
}
