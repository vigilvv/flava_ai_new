import { useState, useEffect, useRef } from "react";
import { ArrowUp, Loader2, Mic, MicOff } from "lucide-react";

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading?: boolean;
}

const ChatInput = ({ onSend, isLoading = false }: ChatInputProps) => {
  const [message, setMessage] = useState("");

  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState("");

  const handleSubmit = () => {
    if (message.trim() && !isLoading) {
      onSend(message);
      setMessage("");
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey && !isLoading) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="relative flex w-full flex-col items-center">
      <div className="relative w-full">
        <textarea
          rows={1}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Message Flava AI"
          className="w-full resize-none rounded-full bg-[#2F2F2F] px-4 py-4 pr-24 focus:outline-none"
          style={{ maxHeight: "200px" }}
          disabled={isLoading}
        />
        <div className="absolute right-3 top-[50%] -translate-y-[50%] flex space-x-2">
          {/* <button
            onClick={isRecording ? stopRecording : startRecording}
            disabled={isLoading}
            className={`p-1.5 rounded-full ${
              isRecording
                ? "bg-red-500 hover:bg-red-600"
                : "bg-white hover:bg-gray-200"
            } disabled:opacity-50 disabled:cursor-not-allowed`}
          >
            {isRecording ? (
              <MicOff className="h-4 w-4 text-white" />
            ) : (
              <Mic className="h-4 w-4 text-black" />
            )}
          </button> */}
          <button
            onClick={handleSubmit}
            disabled={isLoading || !message.trim()}
            className="p-1.5 bg-white rounded-full hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 text-black animate-spin" />
            ) : (
              <ArrowUp className="h-4 w-4 text-black" />
            )}
          </button>
          <p>{transcript}</p>
        </div>
      </div>
    </div>
  );
};

export default ChatInput;
