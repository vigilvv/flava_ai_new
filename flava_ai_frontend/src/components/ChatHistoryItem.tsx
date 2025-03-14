
import { Trash2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface ChatHistoryItemProps {
  title: string;
  isActive: boolean;
  onClick: () => void;
  onDelete: () => void;
}

const ChatHistoryItem = ({
  title,
  isActive,
  onClick,
  onDelete,
}: ChatHistoryItemProps) => {
  const handleDeleteClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onDelete();
  };

  return (
    <div
      className={cn(
        "group flex items-center justify-between gap-2.5 rounded-lg px-2 py-2 cursor-pointer hover:bg-token-sidebar-surface-secondary",
        isActive && "bg-token-sidebar-surface-secondary"
      )}
      onClick={onClick}
    >
      <span className="text-sm truncate flex-1 font-medium">{title}</span>
      <button
        onClick={handleDeleteClick}
        className="p-1 opacity-0 group-hover:opacity-100 hover:bg-gray-700 rounded transition-opacity duration-200"
        aria-label="Delete chat"
      >
        <Trash2 className="h-4 w-4" />
      </button>
    </div>
  );
};

export default ChatHistoryItem;
