import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";
import { Message } from "@/types/chat";

type MessageBubbleProps = {
  message: Message;
};

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export default function MessageBubble({
  message,
}: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div
      className={`flex mb-3 ${
        isUser ? "justify-end" : "justify-start"
      }`}
    >
      <div
        className={`max-w-[70%] rounded-xl px-4 py-2 ${
          isUser
            ? "bg-blue-600 text-white"
            : "bg-gray-200 text-black"
        }`}
      >
        {/* Attachments */}
        {message.attachments &&
          message.attachments.length > 0 && (
            <div
              className={`mb-3 grid gap-2 ${
                message.attachments.length === 1
                  ? "grid-cols-1"
                  : "grid-cols-2"
              }`}
            >
              {message.attachments.map((attachment) => {
                const fileUrl = `${API_URL}/${attachment.storage_path
                  .replace(/\\/g, "/")
                  .replace(/^\/+/, "")}`;

                if (
                  attachment.attachment_type === "image"
                ) {
                  return (
                    <img
                      key={attachment.id}
                      src={fileUrl}
                      alt={attachment.original_name}
                      className="max-h-80 w-full rounded-lg object-cover"
                    />
                  );
                }

                return (
                  <div
                    key={attachment.id}
                    className="rounded-lg border border-white/20 bg-black/10 px-3 py-2 text-sm"
                  >
                    <div className="font-medium">
                      📎 {attachment.original_name}
                    </div>

                    <div className="text-xs opacity-70">
                      {attachment.mime_type}
                    </div>
                  </div>
                );
              })}
            </div>
          )}

        {/* Message text */}
        {message.content && (
          <>
            {isUser ? (
              <p className="whitespace-pre-wrap">
                {message.content}
              </p>
            ) : (
              <ReactMarkdown
                components={{
                  code({
                    className,
                    children,
                    ...props
                  }) {
                    const match =
                      /language-(\w+)/.exec(
                        className || "",
                      );

                    return match ? (
                      <SyntaxHighlighter
                        style={oneDark}
                        language={match[1]}
                        PreTag="div"
                      >
                        {String(children).replace(
                          /\n$/,
                          "",
                        )}
                      </SyntaxHighlighter>
                    ) : (
                      <code
                        className={className}
                        {...props}
                      >
                        {children}
                      </code>
                    );
                  },
                }}
              >
                {message.content}
              </ReactMarkdown>
            )}
          </>
        )}
      </div>
    </div>
  );
}