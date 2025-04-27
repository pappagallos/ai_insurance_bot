'use client';

import React from 'react';

import { ChatMessageEditor } from '../ChatMessageEditor/ChatMessageEditor';
import { ChatEnvironmentProvider, InitChatEnvironmentContextType } from './ChatEnvironmentContext';

import styles from './Chat.module.scss';
import Image from 'next/image';

const initChatEnvironmentContext: InitChatEnvironmentContextType = {
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

interface ChatCompositionProps {
  children: React.ReactNode;
  style?: React.CSSProperties;
}

interface MessageProps {
  htmlMessage?: TrustedHTML;
  textMessage?: string;
}

interface ChatTimeProps {
  date: Date;
}

const ChatTime = ({ date }: ChatTimeProps) => {
  return (
    <div className={styles.chat_time}>
      <p>{date.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })}</p>
    </div>
  );
};

const BotMessage = ({ htmlMessage, textMessage }: MessageProps) => {
  return (
    <div className={styles.bot}>
      <div className={styles.bot_avatar}>
        <img
          src={initChatEnvironmentContext.botAvatar}
          alt={initChatEnvironmentContext.appName}
          className={styles.bot_avatar_image}
        />
      </div>
      <div className={styles.bot_message}>
        <div className={styles.name}>{initChatEnvironmentContext.botName}</div>
        {textMessage && <div className={styles.message}>{textMessage}</div>}
        {htmlMessage && (
          <div
            className={styles.message}
            dangerouslySetInnerHTML={{ __html: htmlMessage as TrustedHTML }}
          />
        )}
      </div>
    </div>
  );
};

const UserMessage = ({ htmlMessage, textMessage }: MessageProps) => {
  return (
    <div className={styles.user}>
      {textMessage && <div className={styles.message}>{textMessage}</div>}
      {htmlMessage && (
        <div
          className={styles.message}
          dangerouslySetInnerHTML={{ __html: htmlMessage as TrustedHTML }}
        />
      )}
    </div>
  );
};

export const Chat = () => {
  return (
    <ChatEnvironmentProvider {...initChatEnvironmentContext}>
      <div className={styles.chat}>
        <Chat.Header>
          <div className={styles.app_content}>
            <div className={styles.app_icon}>
              <Image
                src={initChatEnvironmentContext.appIcon}
                alt={initChatEnvironmentContext.appName}
                width={40}
                height={40}
              />
            </div>
            <div className={styles.app_information}>
              <p className={styles.app_name}>{initChatEnvironmentContext.appName}</p>
              <p className={styles.app_description}>{initChatEnvironmentContext.appDescription}</p>
            </div>
          </div>
        </Chat.Header>
        <Chat.Body>
          <div className={styles.chat_information}>
            <img
              src={initChatEnvironmentContext.appMainImage}
              alt={initChatEnvironmentContext.appName}
              className={styles.app_main_image}
            />
            <p className={styles.chat_title}>{initChatEnvironmentContext.appName}에 문의하기</p>
          </div>
          <div className={styles.chat_history}>
            <ChatTime date={new Date()} />
            <BotMessage htmlMessage={initChatEnvironmentContext.botWelcomeMessage} />
            <UserMessage textMessage={'안녕하세요.'} />
          </div>
        </Chat.Body>
        <Chat.Footer>
          <ChatMessageEditor />
        </Chat.Footer>
      </div>
    </ChatEnvironmentProvider>
  );
};

Chat.Header = ({ children }: ChatCompositionProps) => {
  return <div className={styles.header}>{children}</div>;
};

Chat.Body = ({ children }: ChatCompositionProps) => {
  return <div className={styles.body}>{children}</div>;
};

Chat.Footer = ({ children }: ChatCompositionProps) => {
  return <div className={styles.footer}>{children}</div>;
};

export default Chat;
