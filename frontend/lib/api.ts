const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export async function sendMessage(message: string, chatId: number | null) {
  console.log("message", message);
  const response = await fetch(`${API_URL}/chat`, {
    method: "POST",

    headers: {
      "Content-Type": "application/json",
    },

    body: JSON.stringify({
      chat_id: chatId,
      message,
    }),
  });

  console.log("response", response);

  if (!response.ok) {
    throw new Error("Failed to send message");
  }

  return response.json();
}
