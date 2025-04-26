import { createContext, useMemo } from "react";

export interface ChatEnvironmentContextType {
    messageEditorPlaceholder: string;
}

export interface ChatEnvironmentProviderProps {
    messageEditorPlaceholder: string;
    children: React.ReactNode;
}

export const ChatEnvironmentContext = createContext<ChatEnvironmentContextType | null>(null);

export function ChatEnvironmentProvider({ messageEditorPlaceholder, children }: ChatEnvironmentProviderProps) {
    const value = useMemo(() => {
        return {
            messageEditorPlaceholder,
        }
    }, [messageEditorPlaceholder]);

    return (
        <ChatEnvironmentContext.Provider value={value}>
            {children}
        </ChatEnvironmentContext.Provider>
    );
}