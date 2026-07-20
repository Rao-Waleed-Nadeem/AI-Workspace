import { useEffect, useRef } from "react";
import { Message } from "@/types/chat";
import MessageBubble from "./MessageBubble";

type ChatWindowProps = {
  messages: Message[];
};

export default function ChatWindow({ messages }: ChatWindowProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages]);

  return (
    <div className="border rounded-xl h-96 overflow-y-auto p-4 mb-4">
      {messages.length === 0 && (
        <p className="text-gray-500">Start your first conversation...</p>
      )}

      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}

      <div ref={bottomRef} />
    </div>
  );
}
