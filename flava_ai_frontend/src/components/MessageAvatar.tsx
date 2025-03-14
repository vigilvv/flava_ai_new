
const MessageAvatar = ({ isAssistant }: { isAssistant: boolean }) => {
  if (isAssistant) {
    return (
      <div className="gizmo-shadow-stroke relative flex h-full items-center justify-center rounded-full bg-token-main-surface-primary text-token-text-primary">
        <svg width="41" height="41" viewBox="0 0 512 512" fill="none" xmlns="http://www.w3.org/2000/svg" className="h-2/3 w-2/3" role="img">
          <text x="-9999" y="-9999">Vitruvian Man</text>
          <path d="M256 0C114.6 0 0 114.6 0 256C0 397.4 114.6 512 256 512C397.4 512 512 397.4 512 256C512 114.6 397.4 0 256 0ZM256 40C375.4 40 472 136.6 472 256C472 375.4 375.4 472 256 472C136.6 472 40 375.4 40 256C40 136.6 136.6 40 256 40Z" fill="currentColor" />
          <path d="M256 96L256 416M176 136L336 376M136 176L376 336M96 256L416 256M176 376L336 136M136 336L376 176" stroke="currentColor" strokeWidth="8" strokeLinecap="round" />
          <circle cx="256" cy="256" r="80" stroke="currentColor" strokeWidth="8" fill="none" />
          <path d="M200 180C210 160 230 130 256 130C282 130 302 160 312 180" stroke="currentColor" strokeWidth="8" fill="none" />
          <path d="M200 332C210 352 230 382 256 382C282 382 302 352 312 332" stroke="currentColor" strokeWidth="8" fill="none" />
        </svg>
      </div>
    );
  }
  
  return null;
};

export default MessageAvatar;
