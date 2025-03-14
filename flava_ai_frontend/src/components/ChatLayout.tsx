import { useEffect, useState } from "react";
import Sidebar from "@/components/Sidebar";
import RightSidebar from "@/components/RightSidebar";
import ChatHeader from "@/components/ChatHeader";
import ChatInput from "@/components/ChatInput";
import MessageList from "@/components/MessageList";
import { Chat, Message } from "@/hooks/useChat";

interface ChatLayoutProps {
  chatHistory: Chat[];
  activeChatId: string | null;
  messages: Message[];
  isLoading: boolean;
  mode: "RAG" | "Consensus";
  setMode: React.ComponentState;
  onChatSelect: (id: string) => void;
  onChatDelete: (id: string) => void;
  onNewChat: () => void;
  onSubmit: (message: string) => void;
}

const ChatLayout = ({
  chatHistory,
  activeChatId,
  messages,
  isLoading,
  mode,
  setMode,
  onChatSelect,
  onChatDelete,
  onNewChat,
  onSubmit,
}: ChatLayoutProps) => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isRightSidebarOpen, setIsRightSidebarOpen] = useState(false);

  useEffect(() => {
    if (isRightSidebarOpen) setMode("Consensus");

    if (!isRightSidebarOpen) setMode("RAG");
  }, [isRightSidebarOpen, setMode]);

  return (
    <div className="flex h-screen">
      <Sidebar
        isOpen={isSidebarOpen}
        onToggle={() => setIsSidebarOpen(!isSidebarOpen)}
        chatHistory={chatHistory}
        activeChatId={activeChatId}
        onChatSelect={onChatSelect}
        onChatDelete={onChatDelete}
        onNewChat={onNewChat}
      />

      <main
        className={`flex-1 transition-all duration-300 ${
          isSidebarOpen ? "ml-64" : "ml-0"
        } ${isRightSidebarOpen ? "mr-64" : "mr-0"}`}
      >
        <ChatHeader
          isSidebarOpen={isSidebarOpen}
          isRightSidebarOpen={isRightSidebarOpen}
          onRightSidebarToggle={() =>
            setIsRightSidebarOpen(!isRightSidebarOpen)
          }
          // onNewChat={onNewChat}
        />

        <div
          className={`flex h-full flex-col ${
            messages.length === 0
              ? "items-center justify-center"
              : "justify-between"
          } pt-[60px] pb-4`}
        >
          {messages.length === 0 ? (
            <div className="w-full max-w-3xl px-4 space-y-4">
              <div>
                <h1 className="mb-8 text-4xl font-semibold text-center">
                  Ask me anything about Flare!
                </h1>
                <ChatInput onSend={onSubmit} isLoading={isLoading} />
              </div>
            </div>
          ) : (
            <>
              <MessageList messages={messages} isLoading={isLoading} />
              <div className="w-full max-w-3xl mx-auto px-4 py-2">
                <ChatInput onSend={onSubmit} isLoading={isLoading} />
              </div>
              <div className="text-xs text-center text-gray-500 py-2">
                Flava AI can make mistakes. Check important info.
              </div>
            </>
          )}
        </div>
      </main>

      <RightSidebar
        isOpen={isRightSidebarOpen}
        onToggle={() => setIsRightSidebarOpen(!isRightSidebarOpen)}
      />
    </div>
  );
};

export default ChatLayout;
