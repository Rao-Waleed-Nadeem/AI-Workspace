"use client";

import { useState, useEffect } from "react";
import ChatInput from "@/components/ChatInput";
import ChatWindow from "@/components/ChatWindow";
import {
  sendMessage,
  getChatMessages,
  analyzeMessage,
  sendToolMessage,
  sendVisionMessage,
} from "@/lib/api";
import { Message } from "@/types/chat";
import { useAuth } from "@/lib/useAuth";
import { useRouter } from "next/navigation";

export default function Home() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [chatId, setChatId] = useState<number | null>(null);
  const [action, setAction] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const router = useRouter();

  const { user, loading: authLoading, isAuthenticated } = useAuth();

  useEffect(() => {
    if (!isAuthenticated) {
      return;
    }

    const savedChatId = localStorage.getItem("chatId");

    if (!savedChatId) {
      return;
    }

    const id = Number(savedChatId);

    if (Number.isNaN(id)) {
      localStorage.removeItem("chatId");
      return;
    }

    setChatId(id);

    getChatMessages(id)
      .then((data) => {
        const restoredMessages: Message[] = data.map(
          (message: {
            id: number;
            role: "user" | "assistant";
            content: string;
            attachments?: {
              id: number;
              attachment_type: string;
              original_name: string;
              mime_type: string;
              storage_path: string;
              size: number;
            }[];
          }) => ({
            id: String(message.id),
            role: message.role,
            content: message.content,
            attachments:
              message.attachments?.map((attachment) => ({
                id: attachment.id,
                attachment_type: attachment.attachment_type,
                original_name: attachment.original_name,
                mime_type: attachment.mime_type,
                storage_path: attachment.storage_path,
                size: attachment.size,
              })) ?? [],
          }),
        );

        setMessages(restoredMessages);

        console.log("Restored chat ID:", id);
        console.log("Stored messages:", restoredMessages);
      })
      .catch((error) => {
        console.error("Failed to restore chat:", error);

        localStorage.removeItem("chatId");
        setChatId(null);
        setMessages([]);
      });
  }, [isAuthenticated]);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.replace("/login");
    }
  }, [authLoading, isAuthenticated, router]);

  const handleSend = async () => {
    if ((!input.trim() && !selectedFile) || isLoading) return;

    setIsLoading(true);

    const message = input;

    // Temporary frontend attachment.
    // The negative ID makes it impossible to conflict
    // with a real database attachment ID.
    const temporaryAttachment = selectedFile
      ? {
          id: -Date.now(),
          attachment_type: "image",
          original_name: selectedFile.name,
          mime_type: selectedFile.type,
          storage_path: URL.createObjectURL(selectedFile),
          size: selectedFile.size,
        }
      : undefined;

    const assistantId = crypto.randomUUID();
    const userMessageId = crypto.randomUUID();

    const assistantMessage: Message = {
      id: assistantId,
      role: "assistant",
      content: "",
      attachments: [],
    };

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: message,
      attachments: temporaryAttachment ? [temporaryAttachment] : [],
    };

    setMessages((prev) => [...prev, userMessage, assistantMessage]);

    setInput("");

    try {
      if (selectedFile) {
        const response = await sendVisionMessage(chatId, message, selectedFile);

        // if (response.chat_id !== null) {
        //   setChatId(response.chat_id);
        //   localStorage.setItem("chatId", String(response.chat_id));
        // }

        setMessages((prev) =>
          prev.map((msg) => {
            if (msg.id === userMessageId) {
              return {
                ...msg,
                attachments: response.attachments ?? [],
              };
            }

            if (msg.id === assistantId) {
              return {
                ...msg,
                content: response.message,
              };
            }

            return msg;
          }),
        );

        // ---------------------------------------------
        // Release temporary browser object URL
        // ---------------------------------------------

        if (temporaryAttachment) {
          URL.revokeObjectURL(temporaryAttachment.storage_path);
        }

        setSelectedFile(null);

        setChatId(response.chat_id);
        localStorage.setItem("chatId", String(response.chat_id));

        setSelectedFile(null);

        return;
      } else {
        const { text, chatId: returnedChatId } = await sendMessage(
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

        if (returnedChatId !== null) {
          setChatId(returnedChatId);
          localStorage.setItem("chatId", String(returnedChatId));
        }

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
      }
    } catch (error) {
      console.error(error);

      // Remove optimistic messages if request fails
      setMessages((prev) =>
        prev.filter(
          (msg) => msg.id !== userMessageId && msg.id !== assistantId,
        ),
      );
    } finally {
      setSelectedFile(null);
      setIsLoading(false);
      setAction(null);
    }
  };

  const handleToolTest = async () => {
    if (isLoading) return;

    setIsLoading(true);

    const message = input.trim();

    if (!message) {
      setIsLoading(false);
      return;
    }

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: message,
    };

    setMessages((prev) => [...prev, userMessage]);

    setInput("");

    try {
      const data = await sendToolMessage(message, chatId);

      setChatId(data.chat_id);

      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: data.message,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } finally {
      setIsLoading(false);
    }
  };

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

      if (result.chat_id !== null) {
        setChatId(result.chat_id);

        localStorage.setItem("chatId", String(result.chat_id));
      }
    } finally {
      setIsLoading(false);
    }
  };

  if (authLoading) {
    return (
      <main className="max-w-3xl mx-auto mt-10">
        <p>Checking authentication...</p>
      </main>
    );
  }

  if (!isAuthenticated) {
    return (
      <main className="max-w-3xl mx-auto mt-10">
        <p>Redirecting to login...</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gray-50">
      <div className="max-w-5xl mx-auto px-4 py-6">
        {/* Header */}
        <header className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">AI Workspace</h1>

            <p className="text-sm text-gray-500 mt-1">
              Your personal AI assistant
            </p>
          </div>

          {/* Authentication Actions */}
          <div className="flex items-center gap-3">
            {isAuthenticated ? (
              <>
                <div className="hidden sm:block text-right">
                  <p className="text-sm font-medium text-gray-900">
                    {user?.email}
                  </p>

                  <p className="text-xs text-gray-500">Signed in</p>
                </div>

                <button
                  onClick={() => router.push("/logout")}
                  className="rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 transition hover:bg-gray-100"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <button
                  onClick={() => router.push("/login")}
                  className="rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 transition hover:bg-gray-100"
                >
                  Login
                </button>

                <button
                  onClick={() => router.push("/register")}
                  className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-700"
                >
                  Register
                </button>
              </>
            )}
          </div>
        </header>

        {/* Chat Area */}
        <section className="rounded-2xl border border-gray-200 bg-white shadow-sm">
          <div className="p-5">
            <ChatWindow messages={messages} />
          </div>

          {/* Chat Controls */}
          <div className="border-t border-gray-200 p-5">
            {/* Action Buttons */}
            <div className="flex flex-wrap items-center gap-2 mb-4">
              <button
                onClick={() =>
                  setAction(action === "explain" ? null : "explain")
                }
                disabled={isLoading}
                className={`rounded-lg px-4 py-2 text-sm font-medium transition ${
                  action === "explain"
                    ? "bg-blue-600 text-white hover:bg-blue-700"
                    : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                } disabled:cursor-not-allowed disabled:opacity-50`}
              >
                {action === "explain" ? "Explain: On" : "Explain"}
              </button>
            </div>

            {/* Message Input */}
            <ChatInput
              input={input}
              setInput={setInput}
              selectedFile={selectedFile}
              setSelectedFile={setSelectedFile}
              onSend={handleSend}
              isLoading={isLoading}
            />

            {/* Additional Tools */}
            <div className="flex flex-wrap gap-2 mt-4">
              <button
                onClick={handleAnalyze}
                disabled={!input.trim() || isLoading}
                className="rounded-lg bg-purple-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-purple-700 disabled:cursor-not-allowed disabled:opacity-50"
              >
                Analyze
              </button>

              <button
                onClick={handleToolTest}
                disabled={isLoading}
                className="rounded-lg bg-green-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-green-700 disabled:cursor-not-allowed disabled:opacity-50"
              >
                Test Tool
              </button>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
