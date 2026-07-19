"use client";

import { useState } from "react";
import ChatInput from "@/components/ChatInput";
import ChatWindow from "@/components/ChatWindow";
import { getHelloMessage } from "@/lib/api";

export default function Home() {
  const [input, setInput] = useState("");
  const [message, setMessage] = useState("");

  const handleSend = async () => {
    const data = await getHelloMessage();

    setMessage(data.message);

    setInput("");
  };

  return (
    <main className="max-w-3xl mx-auto mt-10">
      <h1 className="text-3xl font-bold mb-5">AI Workspace</h1>

      <ChatWindow message={message} />

      <ChatInput input={input} setInput={setInput} onSend={handleSend} />
    </main>
  );
}
