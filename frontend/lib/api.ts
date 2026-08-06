import { getAuthHeaders } from "./auth";
import { Attachment } from "../types/attachment";
import { VisionResponse } from "@/types/visionResponse";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export async function sendMessage(
  message: string,
  chatId: number | null,
  onChunk: (chunk: string) => void,
  action: string | null = null,
): Promise<{ text: string; chatId: number | null }> {
  const response = await fetch(`${API_URL}/chat/stream`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({
      chat_id: chatId,
      message,
      action,
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

  let buffer = "";

  // Current SSE event
  let currentEventType = "message";
  let currentEventData: string[] = [];

  const processEvent = () => {
    if (currentEventData.length === 0) {
      currentEventType = "message";
      return;
    }

    // SSE joins multiple data lines with newline characters
    const data = currentEventData.join("\n");

    if (currentEventType === "chat_id") {
      const parsedChatId = Number(data);

      if (!Number.isNaN(parsedChatId)) {
        resolvedChatId = parsedChatId;
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

    buffer += decoder.decode(value, { stream: true });

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

        // SSE removes exactly one optional space after "data:"
        const payload = raw.startsWith(" ") ? raw.slice(1) : raw;

        currentEventData.push(payload);
      }
    }
  }

  // Process any final event that did not receive a trailing blank line
  processEvent();

  return {
    text: fullResponse,
    chatId: resolvedChatId,
  };
}

export async function getChatMessages(chatId: number) {
  const response = await fetch(`${API_URL}/chat/${chatId}/messages`, {
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    throw new Error("Failed to load chat messages");
  }

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
): Promise<VisionResponse> {
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

  const data: VisionResponse = await response.json();

  return data;
}
