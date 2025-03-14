import { useChat } from "@/hooks/useChat";
import ChatLayout from "@/components/ChatLayout";

const Index = () => {
  const {
    chatHistory,
    activeChatId,
    messages,
    isLoading,
    mode,
    setMode,
    handleChatSelect,
    handleChatDelete,
    createNewChat,
    handleSubmit,
  } = useChat();

  return (
    <ChatLayout
      chatHistory={chatHistory}
      activeChatId={activeChatId}
      messages={messages}
      isLoading={isLoading}
      mode={mode}
      setMode={setMode}
      onChatSelect={handleChatSelect}
      onChatDelete={handleChatDelete}
      onNewChat={createNewChat}
      onSubmit={handleSubmit}
    />
  );
};

export default Index;
