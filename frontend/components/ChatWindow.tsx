"use client";

type ChatWindowProps = {
  message: string;
};

export default function ChatWindow({ message }: ChatWindowProps) {
  return (
    <div className="border rounded-lg p-4 h-96 mb-4">
      {message ? (
        <p>{message}</p>
      ) : (
        <p className="text-gray-500">Welcome to AI Workspace</p>
      )}
    </div>
  );
}
