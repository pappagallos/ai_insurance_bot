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
      onClick={disabled ? undefined : onClick}
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

  function clearTextareaHeight() {
    if (!textareaRef.current) return;
    textareaRef.current.style.height = '38px';
  }

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
      onEnter();
      clearTextareaHeight();
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
  disabled: boolean;
}

export const ChatMessageEditor = ({ onSend, disabled }: ChatMessageEditorProps) => {
  const [message, setMessage] = useState<string>('');

  const chatEnvironmentContext = useContext<ChatEnvironmentContextType | null>(
    ChatEnvironmentContext,
  );

  function handleChange(event: React.ChangeEvent<HTMLTextAreaElement>) {
    const value = event.target.value;
    chatEnvironmentContext?.setDisabledSendButton(!value.trim());
    setMessage(value);
  }

  function handleClick() {
    if (disabled) return;
    onSend(message);
    clearMessage();
  }

  function clearMessage() {
    setMessage('');
    chatEnvironmentContext?.setDisabledSendButton(true);
  }

  return (
    <div className={styles.message_editor}>
      <AutoResizeTextarea
        value={message}
        onEnter={handleClick}
        onChange={handleChange}
        placeholder={chatEnvironmentContext?.messageEditorPlaceholder}
      />
      <ChatSendButton
        onClick={handleClick}
        disabled={disabled || (chatEnvironmentContext?.disabledSendButton ?? false)}
      />
    </div>
  );
};
