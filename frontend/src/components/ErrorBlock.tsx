interface ErrorBlockProps {
  message: string;
}

/**
 * Displays a styled error message block.
 * Renders `message` as plain text — never renders raw JSON or objects.
 */
export default function ErrorBlock({ message }: ErrorBlockProps) {
  return (
    <div
      role="alert"
      className="flex items-start gap-2 rounded-md border border-red-400 bg-red-50 px-4 py-3 text-red-700"
    >
      <span className="mt-0.5 shrink-0 text-lg leading-none" aria-hidden="true">
        ⚠
      </span>
      <p className="text-sm font-medium">
        <span className="font-semibold">Error: </span>
        {String(message)}
      </p>
    </div>
  );
}
