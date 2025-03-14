
import { Menu, Plus } from "lucide-react";
import { cn } from "@/lib/utils";
import ChatHistoryItem from "./ChatHistoryItem";

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
  chatHistory: Array<{ id: string; title: string; messages: any[] }>;
  activeChatId: string | null;
  onChatSelect: (id: string) => void;
  onChatDelete: (id: string) => void;
  onNewChat: () => void;
}

const Sidebar = ({
  isOpen,
  onToggle,
  chatHistory,
  activeChatId,
  onChatSelect,
  onChatDelete,
  onNewChat,
}: SidebarProps) => {
  return (
    <div
      className={cn(
        "fixed top-0 left-0 z-40 h-screen bg-chatgpt-sidebar transition-all duration-300",
        isOpen ? "w-64" : "w-0"
      )}
    >
      <nav
        className="flex h-full w-full flex-col px-3"
        aria-label="Chat history"
      >
        <div className="flex justify-between h-[60px] items-center">
          <button
            onClick={onToggle}
            className="h-10 rounded-lg px-2 text-token-text-secondary hover:bg-token-sidebar-surface-secondary"
          >
            <Menu className="h-5 w-5" />
          </button>
          <button 
            onClick={onNewChat}
            className="flex items-center gap-2 rounded-lg px-3 py-1 text-sm hover:bg-token-sidebar-surface-secondary"
          >
            <Plus className="h-5 w-5" />
          </button>
        </div>

        <div className="flex-col flex-1 transition-opacity duration-500 relative -mr-2 pr-2 overflow-y-auto">
          <div className="bg-token-sidebar-surface-primary pt-0">
            <div className="mt-4 flex flex-col gap-2">
              {chatHistory.map((chat) => (
                <ChatHistoryItem
                  key={chat.id}
                  title={chat.title}
                  isActive={chat.id === activeChatId}
                  onClick={() => onChatSelect(chat.id)}
                  onDelete={() => onChatDelete(chat.id)}
                />
              ))}
            </div>
          </div>
        </div>
      </nav>
    </div>
  );
};

export default Sidebar;
