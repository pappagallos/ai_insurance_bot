import { createContext, useMemo, useState } from 'react';

export interface InitChatEnvironmentContextType {
  appName: string;
  appDescription: string;
  appIcon: string;
  appMainImage: string;
  appBackground: string;
  messageEditorPlaceholder: string;
  botName: string;
  botAvatar: string;
  botWelcomeMessage: string;
  disabledSendButton: boolean;
}

export interface ChatEnvironmentContextType extends InitChatEnvironmentContextType {
  setDisabledSendButton: (disabled: boolean) => void;
}

export interface ChatEnvironmentProviderProps extends InitChatEnvironmentContextType {
  children: React.ReactNode;
}

export const ChatEnvironmentContext = createContext<ChatEnvironmentContextType | null>(null);

export function ChatEnvironmentProvider({
  appName,
  appDescription,
  appIcon,
  appMainImage,
  appBackground,
  messageEditorPlaceholder,
  botName,
  botAvatar,
  botWelcomeMessage,
  disabledSendButton: initDisabledSendButton,
  children,
}: ChatEnvironmentProviderProps) {
  const [disabledSendButton, setDisabledSendButton] = useState<boolean>(initDisabledSendButton);

  const value = useMemo(() => {
    return {
      appName,
      appDescription,
      appIcon,
      appMainImage,
      appBackground,
      messageEditorPlaceholder,
      botName,
      botAvatar,
      botWelcomeMessage,
      disabledSendButton,
      setDisabledSendButton,
    };
  }, [
    appName,
    appDescription,
    appIcon,
    appMainImage,
    appBackground,
    messageEditorPlaceholder,
    botName,
    botAvatar,
    botWelcomeMessage,
    disabledSendButton,
  ]);

  return (
    <ChatEnvironmentContext.Provider value={value}>{children}</ChatEnvironmentContext.Provider>
  );
}
