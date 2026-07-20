import { Message } from "@/types/chat";

type MessageBubbleProps = {
  message: Message;
};

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div className={`flex mb-3 ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[70%] rounded-xl px-4 py-2 ${
          isUser ? "bg-blue-600 text-white" : "bg-gray-200 text-black"
        }`}
      >
        {message.content}
      </div>
    </div>
  );
}
