"use client";

import { useState, useEffect } from "react";
import ChatInput from "@/components/ChatInput";
import ChatWindow from "@/components/ChatWindow";
import { sendMessage, getChatMessages } from "@/lib/api";
import { Message } from "@/types/chat";

export default function Home() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [chatId, setChatId] = useState<number | null>(null);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    setIsLoading(true);

    const message = input;

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: message,
    };

    const assistantId = crypto.randomUUID();

    const assistantMessage: Message = {
      id: assistantId,
      role: "assistant",
      content: "",
    };

    setMessages((prev) => [...prev, userMessage, assistantMessage]);

    setInput("");

    try {
      const { text, chatId: newChatId } = await sendMessage(
        message,
        chatId,
        (streamedText) => {
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantId
                ? {
                    ...msg,
                    content: streamedText,
                  }
                : msg,
            ),
          );
        },
      );

      // Persist the chat_id returned by the backend (important for new chats)
      if (newChatId !== null) {
        setChatId(newChatId);
        localStorage.setItem("chatId", String(newChatId));
      }

      // Ensure the final complete text is rendered (guards against partial last chunk)
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === assistantId
            ? {
                ...msg,
                content: text,
              }
            : msg,
        ),
      );
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const savedChatId = localStorage.getItem("chatId");

    if (!savedChatId) return;

    const id = Number(savedChatId);

    setChatId(id);

    getChatMessages(id)
      .then((data) => {
        const restoredMessages: Message[] = data.map(
          (message: {
            id: number;
            role: "user" | "assistant";
            content: string;
          }) => ({
            id: String(message.id),
            role: message.role,
            content: message.content,
          }),
        );

        setMessages(restoredMessages);
      })
      .catch((error) => {
        console.error("Failed to restore chat:", error);

        localStorage.removeItem("chatId");
        setChatId(null);
      });
  }, []);

  return (
    <main className="max-w-3xl mx-auto mt-10">
      <h1 className="text-3xl font-bold mb-5">AI Workspace</h1>

      <ChatWindow messages={messages} />

      <ChatInput
        input={input}
        setInput={setInput}
        onSend={handleSend}
        isLoading={isLoading}
      />
    </main>
  );
}
