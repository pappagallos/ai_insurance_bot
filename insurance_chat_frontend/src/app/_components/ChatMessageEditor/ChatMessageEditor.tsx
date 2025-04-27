import cn from "classnames";

import React, { useState, useContext, useRef } from "react";

import { ChatEnvironmentContext } from "../Chat/ChatEnvironmentContext";
import { ChatEnvironmentContextType } from "../Chat/ChatEnvironmentContext";

import SendIcon from '@mui/icons-material/Send';

import styles from "./ChatMessageEditor.module.scss";

interface ChatSendButtonProps {
    disabled: boolean;
}

export const ChatSendButton = ({ disabled }: ChatSendButtonProps) => {
    return (
        <button className={cn(styles.send_button, {
            [styles.disabled]: disabled,
        })}>
            <SendIcon />
        </button>
    )
}

interface AutoResizeTextareaProps {
    placeholder?: string;
    onChange: (event: React.ChangeEvent<HTMLTextAreaElement>) => void;
}

export const AutoResizeTextarea = ({ placeholder, onChange }: AutoResizeTextareaProps) => {
    const [message, setMessage] = useState<string>('');

    const textareaRef = useRef<HTMLTextAreaElement>(null);
    
    function adjustTextareaHeight() {
        if (!textareaRef.current) return;
        textareaRef.current.style.height = 'auto';
        textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    };

    function handleMessageChange(event: React.ChangeEvent<HTMLTextAreaElement>) {
        onChange(event);
        setMessage(event.target.value);
        adjustTextareaHeight();
    };  

    return (
        <textarea 
            rows={1}
            spellCheck={false}
            autoComplete={"off"}
            value={message} 
            placeholder={placeholder ?? "질문을 입력해 주세요."} 
            onChange={handleMessageChange} 
            ref={textareaRef}
        />
    )
}

export const ChatMessageEditor = () => {
    const chatEnvironmentContext = useContext<ChatEnvironmentContextType | null>(ChatEnvironmentContext);
    
    function onChange(event: React.ChangeEvent<HTMLTextAreaElement>) {
        chatEnvironmentContext?.setDisabledSendButton(!event.target.value.trim());
    }

    return (
        <div className={styles.message_editor}>
            <AutoResizeTextarea onChange={onChange} placeholder={chatEnvironmentContext?.messageEditorPlaceholder} />
            <ChatSendButton disabled={chatEnvironmentContext?.disabledSendButton ?? false} />
        </div>
    )
}