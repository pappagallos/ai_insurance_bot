import cn from "classnames";

import React, { useState, useContext, useRef } from "react";

import { ChatEnvironmentContext } from "../Chat/ChatEnvironmentContext";
import { ChatEnvironmentContextType } from "../Chat/ChatEnvironmentContext";

import SendIcon from '@mui/icons-material/Send';

import styles from "./ChatMessageEditor.module.scss";

export const ChatMessageEditor = () => {
    const chatEnvironmentContext = useContext<ChatEnvironmentContextType | null>(ChatEnvironmentContext);

    const [message, setMessage] = useState<string>('');
    const isEmptyMessage = !message.trim();
    
    const textareaRef = useRef<HTMLTextAreaElement>(null);
    
    const adjustTextareaHeight = () => {
        if (!textareaRef.current) return;
        textareaRef.current.style.height = 'auto';
        textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    };

    const handleMessageChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
        setMessage(event.target.value);
        adjustTextareaHeight();
    };


    return (
        <div className={styles.message_editor}>
            <textarea 
                rows={1}
                spellCheck={false}
                autoComplete={"off"}
                value={message} 
                placeholder={chatEnvironmentContext?.messageEditorPlaceholder} 
                onChange={handleMessageChange} 
                ref={textareaRef}
            />
            <button className={cn(styles.send_button, {
                [styles.disabled]: isEmptyMessage,
            })}>
                <SendIcon />
            </button>
        </div>
    )
}