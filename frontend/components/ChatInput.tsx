import { useRef, useState } from "react";
import { Document } from "@/types/document";

type ChatInputProps = {
  input: string;
  setInput: React.Dispatch<React.SetStateAction<string>>;
  selectedFile: File | null;
  setSelectedFile: React.Dispatch<React.SetStateAction<File | null>>;
  selectedDocumentId: number | null;
  setSelectedDocumentId: React.Dispatch<React.SetStateAction<number | null>>;
  documents: Document[];
  onUploadDocument: (file: File) => Promise<void>;
  onSend: () => void;

  // NEW
  onVoiceMessage: (file: File) => Promise<void>;

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

  // NEW
  onVoiceMessage,

  isLoading,
}: ChatInputProps) {
  const documentInputRef = useRef<HTMLInputElement>(null);

  const imageInputRef = useRef<HTMLInputElement>(null);

  // NEW
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);

  // NEW
  const audioChunksRef = useRef<Blob[]>([]);

  // NEW
  const [isRecording, setIsRecording] = useState(false);

  // NEW
  const handleVoiceToggle = async () => {
    // If already recording, stop it.
    if (isRecording) {
      mediaRecorderRef.current?.stop();
      return;
    }

    // Browser support check.
    if (!navigator.mediaDevices?.getUserMedia) {
      alert("Microphone recording is not supported by this browser.");

      return;
    }

    try {
      // Ask browser for microphone access.
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: true,
      });

      // Record microphone audio as WebM.
      const supportedMimeTypes = [
        "audio/webm;codecs=opus",
        "audio/webm",
        "audio/ogg;codecs=opus",
      ];

      const mimeType = supportedMimeTypes.find((type) =>
        MediaRecorder.isTypeSupported(type),
      );

      if (!mimeType) {
        stream.getTracks().forEach((track) => track.stop());

        alert(
          "This browser does not support a compatible audio recording format.",
        );

        return;
      }

      const mediaRecorder = new MediaRecorder(stream, {
        mimeType,
      });

      // Clear previous recording chunks.
      audioChunksRef.current = [];

      // Browser gives us audio pieces here.
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      // Runs when recorder.stop() is called.
      mediaRecorder.onstop = async () => {
        // Release microphone hardware.
        stream.getTracks().forEach((track) => track.stop());

        // Combine all recorded pieces.
        const audioBlob = new Blob(audioChunksRef.current, {
          type: "audio/webm",
        });

        if (audioBlob.size === 0) {
          setIsRecording(false);
          return;
        }

        // Convert Blob into File.
        const audioFile = new File([audioBlob], `voice-${Date.now()}.webm`, {
          type: "audio/webm",
        });

        try {
          // Send recording to parent.
          await onVoiceMessage(audioFile);
        } finally {
          setIsRecording(false);
        }
      };

      // Start recording.
      mediaRecorder.start();

      mediaRecorderRef.current = mediaRecorder;

      setIsRecording(true);
    } catch (error) {
      console.error("Microphone access failed:", error);

      alert("Microphone permission is required for voice chat.");

      setIsRecording(false);
    }
  };

  return (
    <div className="space-y-3">
      {/* Document selector */}
      <div className="flex items-center gap-2">
        <select
          value={selectedDocumentId ?? ""}
          onChange={(event) => {
            const value = event.target.value;

            setSelectedDocumentId(value ? Number(value) : null);
          }}
          disabled={isLoading}
          className="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm"
        >
          <option value="">Normal Chat</option>

          {documents.map((document) => (
            <option key={document.id} value={document.id}>
              📄 {document.original_name}
            </option>
          ))}
        </select>

        <button
          type="button"
          disabled={isLoading}
          onClick={() => documentInputRef.current?.click()}
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
          Document mode enabled. Your question will be answered using the
          selected PDF.
        </div>
      )}

      {/* Image preview */}
      {selectedFile && (
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <span>🖼️ {selectedFile.name}</span>

          <button
            type="button"
            onClick={() => setSelectedFile(null)}
            disabled={isLoading}
            className="text-red-600 hover:underline"
          >
            Remove
          </button>
        </div>
      )}

      {/* Input */}
      <div className="flex gap-2">
        {/* Existing image button */}
        <button
          type="button"
          disabled={isLoading}
          onClick={() => imageInputRef.current?.click()}
          className="rounded-lg border border-gray-300 bg-white px-3 py-2 hover:bg-gray-100 disabled:opacity-50"
        >
          📎
        </button>

        {/* NEW VOICE BUTTON */}
        <button
          type="button"
          disabled={isLoading}
          onClick={handleVoiceToggle}
          className={`rounded-lg border px-3 py-2 hover:bg-gray-100 disabled:opacity-50 ${
            isRecording
              ? "border-red-400 bg-red-50 text-red-600"
              : "border-gray-300 bg-white"
          }`}
        >
          {isRecording ? "⏹ Stop" : "🎙 Voice"}
        </button>

        <input
          ref={imageInputRef}
          type="file"
          accept="image/png,image/jpeg,image/webp"
          hidden
          onChange={(event) => {
            const file = event.target.files?.[0];

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
          onChange={(event) => setInput(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey) {
              event.preventDefault();
              onSend();
            }
          }}
        />

        <button
          disabled={isLoading || (!input.trim() && !selectedFile)}
          onClick={onSend}
          className="rounded-lg bg-blue-600 px-4 text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isLoading ? "Thinking..." : "Send"}
        </button>
      </div>
    </div>
  );
}
