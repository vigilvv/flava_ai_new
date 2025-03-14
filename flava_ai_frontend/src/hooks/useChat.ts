import { useState, useEffect } from "react";
// import { useToast } from "@/hooks/use-toast";

const STORAGE_KEY = "flavaAI_chatHistory";
// const BACKEND_ROUTE = import.meta.env.VITE_BACKEND_ROUTE;
// const BACKEND_ROUTE = "http://localhost:8080/api/routes/chat/"; // --> for local
const BACKEND_ROUTE = "api/routes/chat/"; // --> for TEE

export type Message = {
  role: "user" | "assistant";
  content: string;
};

export type Chat = {
  id: string;
  title: string;
  messages: Message[];
};

export const useChat = () => {
  const [chatHistory, setChatHistory] = useState<Chat[]>([]);
  const [activeChatId, setActiveChatId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  // const { toast } = useToast();
  const [mode, setMode] = useState<"RAG" | "Consensus">("RAG");

  // Load chat history from local storage on component mount
  useEffect(() => {
    const savedHistory = localStorage.getItem(STORAGE_KEY);
    if (savedHistory) {
      const parsedHistory = JSON.parse(savedHistory);
      setChatHistory(parsedHistory);

      // If history exists, load the most recent chat
      if (parsedHistory.length > 0) {
        const mostRecentChat = parsedHistory[0];
        setActiveChatId(mostRecentChat.id);
        setMessages(mostRecentChat.messages);
      }
    } else {
      // Initialize with an empty chat if no history exists
      createNewChat();
    }
  }, []);

  // Save chat history to local storage whenever it changes
  useEffect(() => {
    if (chatHistory.length > 0) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(chatHistory));
    }
  }, [chatHistory]);

  // Update active chat messages whenever they change
  useEffect(() => {
    if (activeChatId && messages.length > 0) {
      setChatHistory((prevHistory) =>
        prevHistory.map((chat) =>
          chat.id === activeChatId ? { ...chat, messages } : chat
        )
      );
    }
  }, [messages, activeChatId]);

  // Update chat title based on first user message
  useEffect(() => {
    if (activeChatId && messages.length > 0) {
      const firstUserMessage = messages.find((msg) => msg.role === "user");
      if (firstUserMessage) {
        const title = truncateTitle(firstUserMessage.content);
        setChatHistory((prevHistory) =>
          prevHistory.map((chat) =>
            chat.id === activeChatId ? { ...chat, title } : chat
          )
        );
      }
    }
  }, [messages, activeChatId]);

  const truncateTitle = (text: string) => {
    const maxLength = 25;
    return text.length > maxLength
      ? `${text.substring(0, maxLength)}...`
      : text;
  };

  const createNewChat = () => {
    const newChatId = Date.now().toString();
    const newChat: Chat = {
      id: newChatId,
      title: "New Chat",
      messages: [],
    };

    setChatHistory((prev) => [newChat, ...prev]);
    setActiveChatId(newChatId);
    setMessages([]);
  };

  const handleChatSelect = (chatId: string) => {
    const selectedChat = chatHistory.find((chat) => chat.id === chatId);
    if (selectedChat) {
      setActiveChatId(chatId);
      setMessages(selectedChat.messages);
    }
  };

  const handleChatDelete = (chatId: string) => {
    setChatHistory((prev) => prev.filter((chat) => chat.id !== chatId));

    // If deleting the active chat, select another one or create a new one
    if (chatId === activeChatId) {
      const remainingChats = chatHistory.filter((chat) => chat.id !== chatId);
      if (remainingChats.length > 0) {
        handleChatSelect(remainingChats[0].id);
      } else {
        createNewChat();
      }
    }
  };

  const handleSendMessage = async (message: string) => {
    const all_previous_messages = JSON.stringify([
      ...messages.slice(-1),
      { role: "user", content: message },
    ]); // Only taking the last message in the sequence for context

    try {
      const response = await fetch(
        mode === "RAG" ? BACKEND_ROUTE : `${BACKEND_ROUTE}consensus`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ message: all_previous_messages }),
        }
      );

      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      const data = await response.json();
      return data.response;
    } catch (error) {
      console.error("Error:", error);
      return "Sorry, there was an error processing your request. Please try again.";
    }
  };

  const handleSubmit = async (message: string) => {
    setIsLoading(true);
    setMessages((prev) => [...prev, { content: message, role: "user" }]);

    const response = await handleSendMessage(message);
    setMessages((prev) => [...prev, { content: response, role: "assistant" }]);

    setIsLoading(false);
  };

  return {
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
  };
};
