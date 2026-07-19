"use client";

import { useState } from "react";
import ChatInput from "@/components/ChatInput";
import ChatWindow from "@/components/ChatWindow";
import { getHelloMessage } from "@/lib/api";
import { Message } from "@/types/chat";

export default function Home() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: input,
    };

    setMessages((previous) => [...previous, userMessage]);

    setInput("");

    const data = await getHelloMessage();

    const assistantMessage: Message = {
      id: crypto.randomUUID(),
      role: "assistant",
      content: data.message,
    };

    setMessages((previous) => [...previous, assistantMessage]);
  };

  return (
    <main className="max-w-3xl mx-auto mt-10">
      <h1 className="text-3xl font-bold mb-5">AI Workspace</h1>

      <ChatWindow messages={messages} />

      <ChatInput input={input} setInput={setInput} onSend={handleSend} />
    </main>
  );
}
