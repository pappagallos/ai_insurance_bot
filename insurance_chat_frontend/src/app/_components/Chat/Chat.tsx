"use client";

import React from 'react';

import { ChatMessageEditor } from '../ChatMessageEditor/ChatMessageEditor';
import { ChatEnvironmentProvider, ChatEnvironmentContextType } from './ChatEnvironmentContext';

import styles from './Chat.module.scss';

const initChatEnvironmentContext: ChatEnvironmentContextType = {
    messageEditorPlaceholder: '궁금하신 내용을 입력하세요.',
}

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
    )
}

Chat.Footer = ({ children }: ChatFooterProps) => {
    return (
        <div className={styles.footer}>
            {children}
        </div>
    )
}

export default Chat;