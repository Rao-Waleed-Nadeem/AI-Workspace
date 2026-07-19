type ChatInputProps = {
  input: string;
  setInput: React.Dispatch<React.SetStateAction<string>>;
  onSend: () => void;
};

export default function ChatInput({ input, setInput, onSend }: ChatInputProps) {
  return (
    <div className="flex gap-2">
      <input
        className="border rounded-lg p-2 flex-1"
        placeholder="Type your message..."
        value={input}
        onChange={(e) => setInput(e.target.value)}
      />

      <button
        onClick={onSend}
        className="bg-blue-600 text-white px-4 rounded-lg"
      >
        Send
      </button>
    </div>
  );
}
