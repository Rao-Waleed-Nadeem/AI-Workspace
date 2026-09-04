import { useRef } from "react";
import { Document } from "@/lib/api";

type ChatInputProps = {
  input: string;
  setInput: React.Dispatch<React.SetStateAction<string>>;
  selectedFile: File | null;
  setSelectedFile: React.Dispatch<React.SetStateAction<File | null>>;
  selectedDocumentId: number | null;
  setSelectedDocumentId: React.Dispatch<
    React.SetStateAction<number | null>
  >;
  documents: Document[];
  onUploadDocument: (file: File) => Promise<void>;
  onSend: () => void;
  isLoading: boolean;
};

export default function ChatInput({
  input,
  setInput,
  selectedFile,
  setSelectedFile,
  selectedDocumentId,
  setSelectedDocumentId,
  documents,
  onUploadDocument,
  onSend,
  isLoading,
}: ChatInputProps) {
  const documentInputRef =
    useRef<HTMLInputElement>(null);

  const imageInputRef =
    useRef<HTMLInputElement>(null);

  return (
    <div className="space-y-3">

      {/* Document selector */}
      <div className="flex items-center gap-2">

        <select
          value={selectedDocumentId ?? ""}
          onChange={(event) => {
            const value = event.target.value;

            setSelectedDocumentId(
              value ? Number(value) : null,
            );
          }}
          disabled={isLoading}
          className="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm"
        >
          <option value="">
            Normal Chat
          </option>

          {documents.map((document) => (
            <option
              key={document.id}
              value={document.id}
            >
              📄 {document.original_name}
            </option>
          ))}
        </select>

        <button
          type="button"
          disabled={isLoading}
          onClick={() =>
            documentInputRef.current?.click()
          }
          className="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm hover:bg-gray-100 disabled:opacity-50"
        >
          Upload PDF
        </button>

        <input
          ref={documentInputRef}
          type="file"
          accept="application/pdf,.pdf"
          hidden
          onChange={async (event) => {
            const file = event.target.files?.[0];

            if (!file) {
              return;
            }

            await onUploadDocument(file);

            event.target.value = "";
          }}
        />

      </div>

      {/* Selected document */}
      {selectedDocumentId !== null && (
        <div className="rounded-lg bg-blue-50 px-3 py-2 text-sm text-blue-700">
          Document mode enabled. Your question will be
          answered using the selected PDF.
        </div>
      )}

      {/* Image preview */}
      {selectedFile && (
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <span>
            🖼️ {selectedFile.name}
          </span>

          <button
            type="button"
            onClick={() =>
              setSelectedFile(null)
            }
            disabled={isLoading}
            className="text-red-600 hover:underline"
          >
            Remove
          </button>
        </div>
      )}

      {/* Input */}
      <div className="flex gap-2">

        <button
          type="button"
          disabled={isLoading}
          onClick={() =>
            imageInputRef.current?.click()
          }
          className="rounded-lg border border-gray-300 bg-white px-3 py-2 hover:bg-gray-100 disabled:opacity-50"
        >
          📎
        </button>

        <input
          ref={imageInputRef}
          type="file"
          accept="image/png,image/jpeg,image/webp"
          hidden
          onChange={(event) => {
            const file =
              event.target.files?.[0];

            if (!file) {
              return;
            }

            setSelectedFile(file);
            setSelectedDocumentId(null);

            event.target.value = "";
          }}
        />

        <input
          disabled={isLoading}
          className="flex-1 rounded-lg border border-gray-300 p-2"
          placeholder={
            selectedDocumentId !== null
              ? "Ask a question about this document..."
              : "Type your message..."
          }
          value={input}
          onChange={(event) =>
            setInput(event.target.value)
          }
          onKeyDown={(event) => {
            if (
              event.key === "Enter" &&
              !event.shiftKey
            ) {
              event.preventDefault();
              onSend();
            }
          }}
        />

        <button
          disabled={
            isLoading ||
            (!input.trim() && !selectedFile)
          }
          onClick={onSend}
          className="rounded-lg bg-blue-600 px-4 text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isLoading
            ? "Thinking..."
            : "Send"}
        </button>

      </div>
    </div>
  );
}