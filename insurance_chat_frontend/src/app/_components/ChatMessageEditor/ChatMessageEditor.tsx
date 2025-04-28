import cn from 'classnames';

import React, { useState, useContext, useRef } from 'react';

import { ChatEnvironmentContext, ChatEnvironmentContextType } from '../Chat/ChatEnvironmentContext';
import SendIcon from '@mui/icons-material/Send';

import styles from './ChatMessageEditor.module.scss';

interface ChatSendButtonProps {
  disabled: boolean;
  onClick: VoidFunction;
}

export const ChatSendButton = ({ disabled, onClick }: ChatSendButtonProps) => {
  return (
    <button
      className={cn(styles.send_button, {
        [styles.disabled]: disabled,
      })}
      onClick={onClick}
    >
      <SendIcon />
    </button>
  );
};

interface AutoResizeTextareaProps {
  value: string;
  placeholder?: string;
  onChange: (event: React.ChangeEvent<HTMLTextAreaElement>) => void;
  onEnter: VoidFunction;
}

export const AutoResizeTextarea = ({
  value,
  placeholder,
  onChange,
  onEnter,
}: AutoResizeTextareaProps) => {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  function adjustTextareaHeight() {
    if (!textareaRef.current) return;
    textareaRef.current.style.height = 'auto';
    textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
  }

  function handleChange(event: React.ChangeEvent<HTMLTextAreaElement>) {
    onChange(event);
    adjustTextareaHeight();
  }

  function handleKeyUp(event: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (!value.trim()) return;
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      onEnter();
    }
  }

  return (
    <textarea
      rows={1}
      spellCheck={false}
      autoComplete={'off'}
      value={value}
      placeholder={placeholder ?? '질문을 입력해 주세요.'}
      onChange={handleChange}
      onKeyUp={handleKeyUp}
      ref={textareaRef}
    />
  );
};

interface ChatMessageEditorProps {
  onSend: (message: string) => void;
}

export const ChatMessageEditor = ({ onSend }: ChatMessageEditorProps) => {
  const [message, setMessage] = useState<string>('');

  const chatEnvironmentContext = useContext<ChatEnvironmentContextType | null>(
    ChatEnvironmentContext,
  );

  function handleChange(event: React.ChangeEvent<HTMLTextAreaElement>) {
    chatEnvironmentContext?.setDisabledSendButton(!event.target.value.trim());
    setMessage(event.target.value);
  }

  function handleClick() {
    // TODO: 메세지 전송 로직, 서버로부터 LLM Stream 받는 로직 추가
    onSend(message);
    clearMessage();
  }

  function clearMessage() {
    setMessage('');
  }

  return (
    <div className={styles.message_editor}>
      <AutoResizeTextarea
        value={message}
        onChange={handleChange}
        onEnter={handleClick}
        placeholder={chatEnvironmentContext?.messageEditorPlaceholder}
      />
      <ChatSendButton
        onClick={handleClick}
        disabled={chatEnvironmentContext?.disabledSendButton ?? false}
      />
    </div>
  );
};
