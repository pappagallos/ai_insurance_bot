'use client';

import React from 'react';

import { ChatMessageEditor } from '../ChatMessageEditor/ChatMessageEditor';
import { ChatEnvironmentProvider, InitChatEnvironmentContextType } from './ChatEnvironmentContext';

import styles from './Chat.module.scss';

const initChatEnvironmentContext: InitChatEnvironmentContextType = {
  messageEditorPlaceholder: '농협생명보험 AI에게 무엇이든 질문해 주세요.',
  disabledSendButton: true,
};

interface ChatFooterProps {
  children: React.ReactNode;
}

export const Chat = () => {
  return (
    <ChatEnvironmentProvider {...initChatEnvironmentContext}>
      <div className={styles.chat}>
        <Chat.Footer>
          <ChatMessageEditor />
        </Chat.Footer>
      </div>
    </ChatEnvironmentProvider>
  );
};

Chat.Footer = ({ children }: ChatFooterProps) => {
  return <div className={styles.footer}>{children}</div>;
};

export default Chat;
