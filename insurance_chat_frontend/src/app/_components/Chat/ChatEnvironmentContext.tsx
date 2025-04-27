import { createContext, useMemo, useState } from "react";

export interface InitChatEnvironmentContextType {
    messageEditorPlaceholder: string;
    disabledSendButton: boolean;
}

export interface ChatEnvironmentContextType extends InitChatEnvironmentContextType {
    setDisabledSendButton: (disabled: boolean) => void;
}

export interface ChatEnvironmentProviderProps extends InitChatEnvironmentContextType {
    children: React.ReactNode;
}

export const ChatEnvironmentContext = createContext<ChatEnvironmentContextType | null>(null);

export function ChatEnvironmentProvider({ messageEditorPlaceholder, disabledSendButton: initDisabledSendButton, children }: ChatEnvironmentProviderProps) {
    const [disabledSendButton, setDisabledSendButton] = useState<boolean>(initDisabledSendButton);

    const value = useMemo(() => {
        return {
            messageEditorPlaceholder,
            disabledSendButton,
            setDisabledSendButton,
        }
    }, [messageEditorPlaceholder, disabledSendButton]);

    return (
        <ChatEnvironmentContext.Provider value={value}>
            {children}
        </ChatEnvironmentContext.Provider>
    );
}