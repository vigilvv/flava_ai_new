import { useState } from "react";
import ReactMarkdown from "react-markdown";
import MessageAvatar from "./MessageAvatar";
import MessageActions from "./MessageActions";

type MessageProps = {
  role: "user" | "assistant";
  content: string;
};

const Message = ({ role, content }: MessageProps) => {
  // // Extract and remove the specific line
  // const regex = /Agent tool used: retrieve-flare-network-documentation/;
  // const extractedText = content.match(regex)
  //   ? "Agent tool used: retrieve-flare-network-documentation"
  //   : "";
  // const cleanedContent = content.replace(regex, "").trim();

  // Define a regex to match both possible extracted texts
  const regex =
    /Agent tool used: (retrieve-flare-network-documentation|get-validator-info|retrieve-blaze-swap-documentation|get_validator_info)/;

  // Extract the matched text if present
  const match = content.match(regex);
  const extractedText = match ? match[0] : "";

  // Remove the matched text from content
  const cleanedContent = content.replace(regex, "").trim();

  return (
    <div className="py-6">
      <div
        className={`flex gap-4 ${role === "user" ? "flex-row-reverse" : ""}`}
      >
        <MessageAvatar isAssistant={role === "assistant"} />
        <div
          className={`flex-1 space-y-2 ${
            role === "user" ? "flex justify-end" : ""
          }`}
        >
          <div
            className={`${
              role === "user"
                ? "bg-gray-700/50 rounded-[20px] px-4 py-2 inline-block"
                : ""
            }`}
          >
            {role === "user" ? (
              content
            ) : (
              <>
                <div className="prose prose-invert max-w-none">
                  <ReactMarkdown>{cleanedContent}</ReactMarkdown>
                </div>
                {extractedText && (
                  <div className="text-gray-700 italic bg-slate-400 px-3 rounded inline-block">
                    {extractedText}
                  </div>
                )}
              </>
            )}
          </div>
          {role === "assistant" && <MessageActions />}
        </div>
      </div>
    </div>
  );
};

export default Message;
