import cn from 'classnames';
import { marked } from 'marked';
import markedExtendedTables from '@fsegurai/marked-extended-tables';

marked.use(markedExtendedTables());

import React, { forwardRef, useContext, useRef, useState, useEffect } from 'react';
import Image from 'next/image';

import { ChatMessageEditor } from '../ChatMessageEditor/ChatMessageEditor';
import { ChatEnvironmentContext } from './ChatEnvironmentContext';

import styles from './Chat.module.scss';

interface ChatCompositionProps {
  children: React.ReactNode;
  style?: React.CSSProperties;
}

interface MessageProps {
  textMessage?: string;
  htmlMessage?: TrustedHTML;
  isLoading?: boolean;
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

const BotMessage = ({ textMessage, htmlMessage, isLoading }: MessageProps) => {
  const chatEnvironmentContext = useContext(ChatEnvironmentContext);

  return (
    <div className={styles.bot}>
      <div className={styles.bot_avatar}>
        <img
          src={chatEnvironmentContext?.botAvatar}
          alt={chatEnvironmentContext?.appName}
          className={styles.bot_avatar_image}
        />
      </div>
      <div className={styles.bot_message}>
        <div className={styles.name}>{chatEnvironmentContext?.botName}</div>
        {isLoading && (
          <div className={cn(styles.message, styles.loading)}>
            <img src="/assets/bot_loading.svg" alt="bot_loading" />
          </div>
        )}
        {!isLoading && (
          <>
            {textMessage && <span className={styles.message}>{textMessage}</span>}
            {htmlMessage && (
              <div
                className={styles.message}
                dangerouslySetInnerHTML={{
                  __html: marked.parse(htmlMessage as string, {
                    pedantic: true,
                    gfm: true,
                  }),
                }}
              />
            )}
          </>
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
  isLoading?: boolean;
  isMarkdown?: boolean;
}

interface ChatProps {
  chatTrigger: React.ReactNode;
}

export const Chat = ({ chatTrigger }: ChatProps) => {
  const chatEnvironmentContext = useContext(ChatEnvironmentContext);

  const chatHistoryRef = useRef<HTMLDivElement>(null);
  const [chatHistory, setChatHistory] = useState<ChatHistory[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [wasVisible, setWasVisible] = useState<boolean>(false);

  useEffect(() => {
    if (chatEnvironmentContext?.isOpen) setWasVisible(true);
  }, [chatEnvironmentContext?.isOpen]);

  function scrollToBottom() {
    const timeout = setTimeout(() => {
      chatHistoryRef.current?.scrollTo({
        top: chatHistoryRef.current?.scrollHeight,
        behavior: 'smooth',
      });
      clearTimeout(timeout);
    }, 300);
  }

  async function fetchChatResponse(query: string) {
    const response = await fetch('/apis/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'text/event-stream',
      },
      body: JSON.stringify({ query }),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    return response;
  }

  async function processStreamResponse(
    reader: ReadableStreamDefaultReader<Uint8Array>,
    tempId: string,
  ) {
    let accumulatedText = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = new TextDecoder().decode(value);
      accumulatedText = parseChunkAndUpdateChat(chunk, accumulatedText, tempId);
      scrollToBottom();
    }
  }

  function parseChunkAndUpdateChat(chunk: string, accumulatedText: string, tempId: string): string {
    const lines = chunk.split('\n');
    let updatedText = accumulatedText;

    for (const line of lines) {
      if (line.startsWith('data:')) {
        const eventData = line.slice(5).trim();
        if (eventData) {
          try {
            const jsonData = JSON.parse(eventData);
            const content = jsonData.message;
            updatedText += content;
          } catch {
            console.error('Error parsing JSON:', eventData);
          }
        }
      }
    }

    setChatHistory(prev =>
      prev.map(item =>
        item.id === tempId ? { ...item, message: updatedText, isLoading: false } : item,
      ),
    );

    return updatedText;
  }

  function addLoadingBotMessage() {
    const tempId = Date.now().toString();
    setChatHistory(prev => [
      ...prev,
      {
        id: tempId,
        rule: 'bot',
        message: '',
        isLoading: true,
        isMarkdown: true,
      },
    ]);
    return tempId;
  }

  async function streamChat(query: string) {
    setIsLoading(true);

    try {
      const tempId = addLoadingBotMessage();
      scrollToBottom();

      const response = await fetchChatResponse(query);
      const reader = response.body?.getReader();

      if (!reader) throw new Error('No reader available');

      await processStreamResponse(reader, tempId);
    } catch (error) {
      console.error('Error streaming chat:', error);
      // Handle error in UI
      setChatHistory(prev =>
        prev.map(item =>
          item.isLoading
            ? {
                ...item,
                message: '죄송합니다. 요청을 처리하는 중 오류가 발생했습니다.',
                isLoading: false,
              }
            : item,
        ),
      );
    } finally {
      setIsLoading(false);
    }
  }

  async function sleep(ms: number) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  if (chatEnvironmentContext) {
    chatEnvironmentContext.sendMessage = async (message: string) => {
      // 채팅 창 열기
      if (!chatEnvironmentContext?.isOpen) {
        chatEnvironmentContext.setIsOpen(true);
        await sleep(500);
      }
      chatEnvironmentContext.setDisabledSendButton(true);

      // 사용자 메시지 추가
      setChatHistory([
        ...chatHistory,
        {
          id: Date.now().toString(),
          rule: 'user',
          message,
          isLoading: false,
          isMarkdown: false,
        },
      ]);
      scrollToBottom();

      await sleep(1000);

      // 채팅 응답 요청
      await streamChat(message);
    };
  }

  return (
    <React.Fragment>
      {/* 챗봇 트리거 컴포넌트 */}
      {chatTrigger}

      {/* 챗봇 컴포넌트 */}
      <div
        className={cn(styles.chat, {
          [styles.visible]: chatEnvironmentContext?.isOpen,
          [styles.was_visible]: wasVisible && !chatEnvironmentContext?.isOpen,
        })}
      >
        <Chat.Header>
          <div className={styles.app_content}>
            <div className={styles.app_icon}>
              <Image
                src={chatEnvironmentContext?.appIcon as string}
                alt={chatEnvironmentContext?.appName as string}
                width={40}
                height={40}
              />
            </div>
            <div className={styles.app_information}>
              <p className={styles.app_name}>{chatEnvironmentContext?.appName}</p>
              <p className={styles.app_description}>{chatEnvironmentContext?.appDescription}</p>
            </div>
          </div>
        </Chat.Header>
        <Chat.Body ref={chatHistoryRef}>
          <div className={styles.chat_information}>
            <img
              src={chatEnvironmentContext?.appMainImage}
              alt={chatEnvironmentContext?.appName}
              className={styles.app_main_image}
            />
            <p className={styles.chat_title}>{chatEnvironmentContext?.appName}에 문의하기</p>
          </div>
          <div className={styles.chat_history}>
            <ChatTime date={new Date()} />
            <BotMessage htmlMessage={chatEnvironmentContext?.botWelcomeMessage} />
            {chatHistory.map((chat, index) => {
              if (chat.rule === 'user')
                return <UserMessage textMessage={chat.message as string} key={index} />;
              else
                return (
                  <BotMessage
                    htmlMessage={chat.message as TrustedHTML}
                    isLoading={chat.isLoading}
                    key={index}
                  />
                );
            })}
          </div>
        </Chat.Body>
        <Chat.Footer>
          <ChatMessageEditor
            onSend={message => {
              setChatHistory([
                ...chatHistory,
                {
                  rule: 'user',
                  message,
                  id: Date.now().toString(),
                  isLoading: false,
                  isMarkdown: false,
                },
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
    </React.Fragment>
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
