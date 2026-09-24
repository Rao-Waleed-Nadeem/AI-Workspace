import { getAuthHeaders } from "./auth";
import { Attachment } from "../types/attachment";
import { Document } from "../types/document";
import { Memory } from "../types/memory";
import { GeneratedImage } from "../types/generatedImage";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export async function sendMessage(
  message: string,
  chatId: number | null,
  onChunk: (chunk: string) => void,
  action: string | null = null,
  documentId: number | null = null,
  onSources?: (
    sources: {
      document_id: number;
      document_name: string;
      page_number: number | null;
    }[],
  ) => void,
): Promise<{
  text: string;
  chatId: number | null;
  sources: {
    document_id: number;
    document_name: string;
    page_number: number | null;
  }[];
}> {
  const response = await fetch(`${API_URL}/chat/stream`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({
      chat_id: chatId,
      message,
      action,
      document_id: documentId,
    }),
  });

  if (!response.ok) {
    throw new Error("Failed to send message");
  }

  if (!response.body) {
    throw new Error("Response body is empty");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  let fullResponse = "";
  let resolvedChatId: number | null = null;
  let receivedSources: {
    document_id: number;
    document_name: string;
    page_number: number | null;
  }[] = [];

  let buffer = "";

  let currentEventType = "message";
  let currentEventData: string[] = [];

  const processEvent = () => {
    if (currentEventData.length === 0) {
      currentEventType = "message";
      return;
    }

    const data = currentEventData.join("\n");

    if (currentEventType === "chat_id") {
      const parsedChatId = Number(data);

      if (!Number.isNaN(parsedChatId)) {
        resolvedChatId = parsedChatId;
      }
    } else if (currentEventType === "sources") {
      try {
        receivedSources = JSON.parse(data);
      } catch (error) {
        console.error("Failed to parse RAG sources:", error);
      }
    } else if (
      currentEventType === "rag_error" ||
      currentEventType === "stream_error"
    ) {
      try {
        const errorMessage = JSON.parse(data);

        fullResponse = errorMessage;

        onChunk(fullResponse);
      } catch (error) {
        console.error("Failed to parse RAG error:", error);

        fullResponse = data;

        onChunk(fullResponse);
      }
    } else {
      fullResponse += data;

      onChunk(fullResponse);
    }

    currentEventData = [];
    currentEventType = "message";
  };

  while (true) {
    const { done, value } = await reader.read();

    if (done) {
      break;
    }

    buffer += decoder.decode(value, {
      stream: true,
    });

    const lines = buffer.split("\n");

    buffer = lines.pop() ?? "";

    for (const line of lines) {
      const normalizedLine = line.replace(/\r$/, "");

      // Blank line = end of SSE event
      if (normalizedLine === "") {
        processEvent();
        continue;
      }

      if (normalizedLine.startsWith("event:")) {
        currentEventType = normalizedLine.slice("event:".length).trim();

        continue;
      }

      if (normalizedLine.startsWith("data:")) {
        const raw = normalizedLine.slice("data:".length);

        // Remove exactly one optional space.
        const payload = raw.startsWith(" ") ? raw.slice(1) : raw;

        currentEventData.push(payload);
      }
    }
  }

  // Process any final event that does not have
  // a trailing blank line.
  processEvent();

  return {
    text: fullResponse,
    chatId: resolvedChatId,
    sources: receivedSources,
  };
}

export async function getDocuments(): Promise<Document[]> {
  const response = await fetch(`${API_URL}/files`, {
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    throw new Error("Failed to load documents");
  }

  const data = await response.json();

  return data.documents;
}

export async function uploadDocument(file: File): Promise<Document> {
  const formData = new FormData();

  formData.append("file", file);

  const authHeaders = getAuthHeaders();

  delete authHeaders["Content-Type"];

  const response = await fetch(`${API_URL}/files/upload`, {
    method: "POST",
    headers: authHeaders,
    body: formData,
  });

  if (!response.ok) {
    const errorText = await response.text();

    console.error("Document upload error:", errorText);

    throw new Error("Failed to upload document");
  }

  const data = await response.json();

  return data.document;
}

export async function getChatMessages(chatId: number) {
  const response = await fetch(`${API_URL}/chat/${chatId}/messages`, {
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    throw new Error("Failed to load chat messages");
  }

  // console.log("getChatMessages response", response);

  return response.json();
}

export async function analyzeMessage(
  message: string,
  chatId: number | null,
): Promise<{
  chat_id: number | null;
  title: string;
  summary: string;
  keywords: string[];
}> {
  const response = await fetch(`${API_URL}/chat/structured`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({
      chat_id: chatId,
      message,
    }),
  });

  if (!response.ok) {
    throw new Error("Failed to analyze message");
  }

  return response.json();
}

export async function sendToolMessage(message: string, chatId: number | null) {
  const response = await fetch(`${API_URL}/chat/tools`, {
    method: "POST",

    headers: getAuthHeaders(),

    body: JSON.stringify({
      chat_id: chatId,
      action: "",
      message,
    }),
  });

  if (!response.ok) {
    const errorText = await response.text();

    console.error("Tool API error:", errorText);

    throw new Error("Failed to send tool message");
  }

  return response.json();
}

export async function sendVisionMessage(
  chatId: number | null,
  message: string,
  image: File,
): Promise<{ chat_id: number; message: string; attachments: Attachment[] }> {
  const formData = new FormData();

  formData.append("message", message);

  if (chatId !== null) {
    formData.append("chat_id", chatId.toString());
  }

  formData.append("image", image);

  const authHeaders = getAuthHeaders();
  delete authHeaders["Content-Type"];

  const response = await fetch(`${API_URL}/chat/vision`, {
    method: "POST",
    headers: authHeaders,
    body: formData,
  });

  if (!response.ok) {
    throw new Error("Failed to send vision message");
  }

  const data = await response.json();

  console.log("Vision API response:", data);

  return data;
}

export async function getMemories(): Promise<Memory[]> {
  const response = await fetch(`${API_URL}/memory`, {
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    throw new Error("Failed to load memories");
  }

  return response.json();
}

export async function deleteMemory(memoryId: number): Promise<void> {
  const response = await fetch(`${API_URL}/memory/${memoryId}`, {
    method: "DELETE",
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    throw new Error("Failed to delete memory");
  }
}

export async function clearMemories(): Promise<{
  deleted_count: number;
}> {
  const response = await fetch(`${API_URL}/memory`, {
    method: "DELETE",
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    throw new Error("Failed to clear memories");
  }

  return response.json();
}

export async function generateImage(
  prompt: string,
): Promise<GeneratedImage> {
  const response = await fetch(
    `${API_URL}/images/generate`,
    {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({
        prompt,
      }),
    },
  );

  if (!response.ok) {
    const errorText = await response.text();

    console.error(
      "Image generation error:",
      errorText,
    );

    throw new Error(
      "Failed to generate image",
    );
  }

  return response.json();
}

export async function fetchGeneratedImage(
  imageUrl: string,
): Promise<Blob> {
  const response = await fetch(`${API_URL}${imageUrl}`, {
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    throw new Error("Failed to load generated image");
  }

  return response.blob();
}

export async function transcribeAudio(
  file: File,
): Promise<{ transcript: string }> {
  const formData = new FormData();

  formData.append("file", file);

  const authHeaders = getAuthHeaders();

  delete authHeaders["Content-Type"];

  const response = await fetch(
    `${API_URL}/speech/transcribe`,
    {
      method: "POST",
      headers: authHeaders,
      body: formData,
    },
  );

  if (!response.ok) {
    const errorText = await response.text();

    console.error(
      "Speech-to-text error:",
      errorText,
    );

    throw new Error(
      "Failed to transcribe audio",
    );
  }

  return response.json();
}

export async function synthesizeSpeech(
  text: string,
): Promise<{
  audio_chunks: string[];
}> {

  const response = await fetch(
    `${API_URL}/speech/synthesize`,
    {
      method: "POST",

      headers: getAuthHeaders(),

      body: JSON.stringify({
        text,
      }),
    },
  );

  if (!response.ok) {

    const errorText =
      await response.text();

    console.error(
      "Text-to-speech error:",
      errorText,
    );

    throw new Error(
      "Failed to generate speech",
    );
  }

  return response.json();
}

