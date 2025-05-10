'use client';

import { createContext, useMemo, useState } from 'react';

export interface InitChatEnvironmentContextType {
  isOpen: boolean;
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
  sendMessage: (message: string) => void;
}

export interface ChatEnvironmentContextType extends InitChatEnvironmentContextType {
  setIsOpen: (isOpen: boolean) => void;
  setDisabledSendButton: (disabled: boolean) => void;
}

export interface ChatEnvironmentProviderProps extends InitChatEnvironmentContextType {
  children: React.ReactNode;
}

export const ChatEnvironmentContext = createContext<ChatEnvironmentContextType | null>(null);

export function ChatEnvironmentProvider({
  isOpen: initIsOpen,
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
  sendMessage,
  children,
}: ChatEnvironmentProviderProps) {
  const [isOpen, setIsOpen] = useState<boolean>(initIsOpen);
  const [disabledSendButton, setDisabledSendButton] = useState<boolean>(initDisabledSendButton);

  const value = useMemo(() => {
    return {
      isOpen,
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
      setIsOpen,
      setDisabledSendButton,
      sendMessage,
    };
  }, [
    isOpen,
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
    sendMessage,
  ]);

  return (
    <ChatEnvironmentContext.Provider value={value}>{children}</ChatEnvironmentContext.Provider>
  );
}
