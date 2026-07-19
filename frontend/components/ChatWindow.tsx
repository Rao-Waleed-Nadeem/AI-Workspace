import { Message } from "@/types/chat";

type ChatWindowProps = {
  messages: Message[];
};

export default function ChatWindow({ messages }: ChatWindowProps) {
  return (
    <div className="border rounded-lg p-4 h-96 overflow-y-auto mb-4">
      {messages.length === 0 && (
        <p className="text-gray-500">Welcome to AI Workspace</p>
      )}

      {messages.map((message) => (
        <div key={message.id} className="mb-3">
          <strong>{message.role === "user" ? "You" : "AI"}</strong>

          <p>{message.content}</p>
        </div>
      ))}
    </div>
  );
}
