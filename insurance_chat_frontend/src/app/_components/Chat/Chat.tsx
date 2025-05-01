'use client';

import React, { forwardRef, useRef, useState } from 'react';

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
        {textMessage && <span className={styles.message}>{textMessage}</span>}
        {htmlMessage && (
          <span className={styles.message} dangerouslySetInnerHTML={{ __html: htmlMessage }} />
        )}
      </div>
    </div>
  );
};

const UserMessage = ({ htmlMessage, textMessage }: MessageProps) => {
  return (
    <div className={styles.user}>
      {textMessage && <span className={styles.message}>{textMessage}</span>}
      {htmlMessage && (
        <span
          className={styles.message}
          dangerouslySetInnerHTML={{ __html: htmlMessage as TrustedHTML }}
        />
      )}
    </div>
  );
};

interface ChatHistory {
  id: string;
  rule: 'user' | 'bot';
  message: string | React.JSX.Element;
}

export const Chat = () => {
  const chatHistoryRef = useRef<HTMLDivElement>(null);
  const [chatHistory, setChatHistory] = useState<ChatHistory[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  function scrollToBottom() {
    const timeout = setTimeout(() => {
      chatHistoryRef.current?.scrollTo({
        top: chatHistoryRef.current?.scrollHeight,
        behavior: 'smooth',
      });
      clearTimeout(timeout);
    }, 300);
  }

  async function streamChat(query: string) {
    setIsLoading(true);

    try {
      const tempId = Date.now().toString();
      setChatHistory(prev => [
        ...prev,
        {
          rule: 'bot',
          message: <img src="/assets/bot_loading.svg" alt="bot_loading" />,
          id: tempId,
        },
      ]);
      scrollToBottom();

      const response = await fetch('/apis/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'text/event-stream',
        },
        body: JSON.stringify({ query }),
      });

      const reader = response.body?.getReader();
      if (!reader) throw new Error('No reader available');

      let accumulatedText = '';

      while (true) {
        const { done, value } = await reader.read();

        if (done) {
          break;
        }

        const chunk = new TextDecoder().decode(value);

        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data:')) {
            const eventData = line.slice(5).trim();
            if (eventData) {
              try {
                const jsonData = JSON.parse(eventData);
                console.log(jsonData);
                const content = jsonData.chat;
                accumulatedText += content;
              } catch {
                console.error('Error parsing JSON:', eventData);
              }
            }
          }
        }

        setChatHistory(prev =>
          prev.map(item => (item.id === tempId ? { ...item, message: accumulatedText } : item)),
        );
        scrollToBottom();
      }
    } catch (error) {
      console.error('Error streaming chat:', error);
    } finally {
      setIsLoading(false);
    }
  }

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
        <Chat.Body ref={chatHistoryRef}>
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
            {chatHistory.map((chat, index) => {
              const MessageComponent = chat.rule === 'user' ? UserMessage : BotMessage;
              if (chat.message instanceof HTMLElement)
                return <MessageComponent htmlMessage={chat.message as TrustedHTML} key={index} />;
              return <MessageComponent textMessage={chat.message as string} key={index} />;
            })}
          </div>
        </Chat.Body>
        <Chat.Footer>
          <ChatMessageEditor
            onSend={message => {
              setChatHistory([
                ...chatHistory,
                { rule: 'user', message, id: Date.now().toString() },
              ]);
              const timeout = setTimeout(() => {
                streamChat(message);
                clearTimeout(timeout);
                scrollToBottom();
              }, 1000);
              scrollToBottom();
            }}
            disabled={isLoading}
          />
        </Chat.Footer>
      </div>
    </ChatEnvironmentProvider>
  );
};

Chat.Header = ({ children }: ChatCompositionProps) => {
  return <div className={styles.header}>{children}</div>;
};

Chat.Body = forwardRef<HTMLDivElement, ChatCompositionProps>(({ children }, ref) => {
  return (
    <div className={styles.body} ref={ref}>
      {children}
    </div>
  );
});

Chat.Footer = ({ children }: ChatCompositionProps) => {
  return <div className={styles.footer}>{children}</div>;
};

export default Chat;
