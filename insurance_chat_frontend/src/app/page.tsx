'use client';

import React, { useContext } from 'react';

// Components
import Chat from './_components/Chat/Chat';
import ChatTriggerButton from './_components/ChatTriggerButton/ChatTriggerButton';
import {
  ChatEnvironmentContext,
  ChatEnvironmentProvider,
  InitChatEnvironmentContextType,
} from './_components/Chat/ChatEnvironmentContext';

const context: InitChatEnvironmentContextType = {
  isOpen: false,
  appName: process.env.NEXT_PUBLIC_APP_NAME as string,
  appDescription: process.env.NEXT_PUBLIC_APP_DESCRIPTION as string,
  appIcon: process.env.NEXT_PUBLIC_APP_ICON as string,
  appMainImage: process.env.NEXT_PUBLIC_APP_MAIN_IMAGE as string,
  appBackground: process.env.NEXT_PUBLIC_APP_BACKGROUND_IMAGE as string,
  messageEditorPlaceholder: process.env.NEXT_PUBLIC_MESSAGE_EDITOR_PLACEHOLDER as string,
  botName: process.env.NEXT_PUBLIC_BOT_NAME as string,
  botAvatar: process.env.NEXT_PUBLIC_BOT_AVATAR as string,
  botWelcomeMessage: process.env.NEXT_PUBLIC_BOT_WELCOME_MESSAGE as string,
  disabledSendButton: true,
};

export default function Page() {
  return (
    <ChatEnvironmentProvider {...context}>
      <ChatComponent />
    </ChatEnvironmentProvider>
  );
}

export const ChatComponent = () => {
  const chatEnvironmentContext = useContext(ChatEnvironmentContext);

  return (
    <Chat
      chatTrigger={
        <ChatTriggerButton
          onClick={() => chatEnvironmentContext?.setIsOpen(!chatEnvironmentContext?.isOpen)}
        />
      }
    />
  );
};
