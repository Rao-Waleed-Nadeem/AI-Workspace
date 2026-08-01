"use client";

import { useState, useEffect } from "react";
import ChatInput from "@/components/ChatInput";
import ChatWindow from "@/components/ChatWindow";
import { sendMessage, getChatMessages, analyzeMessage } from "@/lib/api";
import { Message } from "@/types/chat";

export default function Home() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [chatId, setChatId] = useState<number | null>(null);
  const [action, setAction] = useState<string | null>(null);

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
        action,
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
      setAction(null);
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

  const handleAnalyze = async () => {
    if (!input.trim() || isLoading) return;

    setIsLoading(true);

    const message = input;

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: message,
    };

    setMessages((prev) => [...prev, userMessage]);

    setInput("");

    try {
      const result = await analyzeMessage(message, chatId);

      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: `## ${result.title}\n\n${result.summary}\n\n**Keywords:** ${result.keywords.join(", ")}`,
      };

      setMessages((prev) => [...prev, assistantMessage]);

      // The structured endpoint creates a chat when chatId is null.
      // We need the backend to return chat_id for this to be persisted.
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="max-w-3xl mx-auto mt-10">
      <h1 className="text-3xl font-bold mb-5">AI Workspace</h1>

      <ChatWindow messages={messages} />
      <button
        onClick={() => setAction(action === "explain" ? null : "explain")}
        disabled={isLoading}
        className={`mb-4 cursor-pointer  rounded-lg px-4 py-2 ${
          action === "explain"
            ? "bg-blue-600 hover:bg-blue-700 text-white"
            : "bg-gray-200 hover:bg-gray-400 text-black"
        }`}
      >
        Explain
      </button>

      <ChatInput
        input={input}
        setInput={setInput}
        onSend={handleSend}
        isLoading={isLoading}
      />
      <button
        onClick={handleAnalyze}
        disabled={!input.trim() || isLoading}
        className="px-4 py-2 rounded-lg bg-purple-600 text-white disabled:opacity-50"
      >
        Analyze
      </button>
    </main>
  );
}
