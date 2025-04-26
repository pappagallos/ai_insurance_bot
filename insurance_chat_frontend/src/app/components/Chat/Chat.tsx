"use client";

import React, { useContext, useState } from 'react';

import { ChatEnvironmentProvider, ChatEnvironmentContextType, ChatEnvironmentContext } from './ChatEnvironmentContext';

import styles from './Chat.module.scss';

const initChatEnvironmentContext: ChatEnvironmentContextType = {
    messageEditorPlaceholder: '궁금하신 내용을 입력하세요.',
}

const ChatMessageEditor = () => {
    const chatEnvironmentContext = useContext<ChatEnvironmentContextType | null>(ChatEnvironmentContext);

    const [message, setMessage] = useState<string>('');

    return (
        <div className={styles.message_editor}>
            <textarea placeholder={chatEnvironmentContext?.messageEditorPlaceholder} value={message} onChange={(event) => setMessage(event.target.value)} />
        </div>
    )
}

export const Chat = () => {
    return (
        <div className={styles.chat}>
            <ChatEnvironmentProvider {...initChatEnvironmentContext}>
                <ChatMessageEditor />
            </ChatEnvironmentProvider>
        </div>
    )
}

export default Chat;