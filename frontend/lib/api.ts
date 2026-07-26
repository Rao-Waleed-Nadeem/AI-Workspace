const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export async function sendMessage(
  message: string,
  chatId: number | null,
  onChunk: (chunk: string) => void,
): Promise<{ text: string; chatId: number | null }> {
  const response = await fetch(`${API_URL}/chat/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      chat_id: chatId,
      message,
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

  // SSE parsing state — buffer incomplete lines between chunks
  let buffer = "";
  let currentEventType = "message"; // default SSE event type

  while (true) {
    const { done, value } = await reader.read();

    if (done) break;

    // Append decoded bytes to our running line buffer
    buffer += decoder.decode(value, { stream: true });

    // Split on newlines; keep the last (possibly incomplete) fragment
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      const trimmed = line.replace(/\r$/, ""); // strip only CR; preserve trailing spaces (they are valid token content)

      if (trimmed === "") {
        // Blank line signals end of an SSE event; reset event type
        currentEventType = "message";
        continue;
      }

      if (trimmed.startsWith("event:")) {
        // Named event — store for the next data line
        currentEventType = trimmed.slice("event:".length).trim();
        continue;
      }

      if (trimmed.startsWith("data:")) {
        // Per SSE spec: remove at most one space after "data:" — preserve all other whitespace (token spaces)
        const raw = trimmed.slice("data:".length);
        const payload = raw.startsWith(" ") ? raw.slice(1) : raw;

        if (currentEventType === "chat_id") {
          resolvedChatId = parseInt(payload, 10);
        } else {
          // Regular text token — accumulate and stream to UI
          fullResponse += payload;
          onChunk(fullResponse);
        }
      }
    }
  }

  return { text: fullResponse, chatId: resolvedChatId };
}
