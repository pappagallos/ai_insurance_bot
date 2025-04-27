import React, { useState, useContext, useRef } from "react";

import { ChatEnvironmentContext } from "../Chat/ChatEnvironmentContext";
import { ChatEnvironmentContextType } from "../Chat/ChatEnvironmentContext";

import styles from "./ChatMessageEditor.module.scss";

export const ChatMessageEditor = () => {
    const chatEnvironmentContext = useContext<ChatEnvironmentContextType | null>(ChatEnvironmentContext);

    const [message, setMessage] = useState<string>('');
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
        </div>
    )
}