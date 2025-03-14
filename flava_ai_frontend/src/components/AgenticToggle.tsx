import { useState } from "react";
import { Switch } from "@/components/ui/switch";

export default function AgenticToggle() {
  const [isAgenticRAG, setIsAgenticRAG] = useState(true);

  return (
    <div className="flex items-center gap-4">
      <span className={isAgenticRAG ? "font-bold" : "text-gray-500"}>
        Agentic RAG
      </span>
      <Switch
        checked={!isAgenticRAG}
        onCheckedChange={() => setIsAgenticRAG((prev) => !prev)}
      />
      <span className={!isAgenticRAG ? "font-bold" : "text-gray-500"}>
        Agentic Consensus
      </span>
    </div>
  );
}
