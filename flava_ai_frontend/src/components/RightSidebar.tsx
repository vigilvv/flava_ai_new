import { ChevronLeft } from "lucide-react";
import { cn } from "@/lib/utils";

interface RightSidebarProps {
  isOpen: boolean;
  onToggle: () => void;
}

const RightSidebar = ({ isOpen, onToggle }: RightSidebarProps) => {
  return (
    <div
      className={cn(
        "fixed top-0 right-0 z-40 h-screen bg-chatgpt-sidebar transition-all duration-300",
        isOpen ? "w-64" : "w-0"
      )}
    >
      <nav
        className="flex h-full w-full flex-col px-3"
        aria-label="Secondary navigation"
      >
        <div className="flex justify-between h-[60px] items-center">
          <button
            onClick={onToggle}
            className="h-10 rounded-lg px-2 text-token-text-secondary hover:bg-token-sidebar-surface-secondary"
          >
            <div className="flex text-sm bg-gray-300 text-black rounded px-2 py-2">
              <ChevronLeft className="h-5 w-5" /> <p>Close Consensus mode</p>
            </div>
          </button>
        </div>

        <div className="flex-col flex-1 transition-opacity duration-500 relative -mr-2 pr-2 overflow-y-auto">
          {isOpen && (
            <div className="bg-token-sidebar-surface-primary">
              <div className="mt-4 flex flex-col gap-4">
                <div className="px-3 py-2 text-xs text-gray-300">
                  Consensus mode runs multiple agents in parallel and then
                  aggregates responses. Please be patient.
                </div>
                {/* <div className="group flex h-10 items-center gap-2.5 rounded-lg px-2 hover:bg-token-sidebar-surface-secondary cursor-pointer">
                  <span className="text-sm">API Documentation</span>
                </div>
                <div className="group flex h-10 items-center gap-2.5 rounded-lg px-2 hover:bg-token-sidebar-surface-secondary cursor-pointer">
                  <span className="text-sm">Guides & Tutorials</span>
                </div>
                <div className="group flex h-10 items-center gap-2.5 rounded-lg px-2 hover:bg-token-sidebar-surface-secondary cursor-pointer">
                  <span className="text-sm">Code Samples</span>
                </div> */}
              </div>
            </div>
          )}
        </div>
      </nav>
    </div>
  );
};

export default RightSidebar;
