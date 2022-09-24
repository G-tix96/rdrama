import React, {
  createContext,
  PropsWithChildren,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { io, Socket } from "socket.io-client";
import lozad from "lozad";
import { useRootContext } from "./useRootContext";
import { useWindowFocus } from "./useWindowFocus";

enum ChatHandlers {
  CONNECT = "connect",
  CATCHUP = "catchup",
  ONLINE = "online",
  TYPING = "typing",
  DELETE = "delete",
  SPEAK = "speak",
}

interface ChatProviderContext {
  online: string[];
  typing: string[];
  messages: ChatSpeakResponse[];
  draft: string;
  quote: null | ChatSpeakResponse;
  updateDraft: React.Dispatch<React.SetStateAction<string>>;
  sendMessage(): void;
  quoteMessage(message: null | ChatSpeakResponse): void;
  deleteMessage(withText: string): void;
}

const ChatContext = createContext<ChatProviderContext>({
  online: [],
  typing: [],
  messages: [],
  draft: "",
  quote: null,
  updateDraft() {},
  sendMessage() {},
  quoteMessage() {},
  deleteMessage() {},
});

export function ChatProvider({ children }: PropsWithChildren) {
  const { username, siteName } = useRootContext();
  const socket = useRef<null | Socket>(null);
  const [online, setOnline] = useState<string[]>([]);
  const [typing, setTyping] = useState<string[]>([]);
  const [messages, setMessages] = useState<ChatSpeakResponse[]>([]);
  const [draft, setDraft] = useState("");
  const [quote, setQuote] = useState<null | ChatSpeakResponse>(null);
  const focused = useWindowFocus();
  const [notifications, setNotifications] = useState<number>(0);
  const addMessage = useCallback((message: ChatSpeakResponse) => {
    setMessages((prev) => prev.concat(message));
    
    if (message.username !== username && !document.hasFocus()) {
      setNotifications((prev) => prev + 1);
    }
  }, []);
  const sendMessage = useCallback(() => {
    const message = quote
      ? `> ${quote.text}\n@${quote.username}<br /><br />${draft}`
      : draft;
    socket.current?.emit(ChatHandlers.SPEAK, message);

    setQuote(null);
    setDraft("");
  }, [draft]);
  const requestDeleteMessage = useCallback((withText: string) => {
    socket.current?.emit(ChatHandlers.DELETE, withText);
  }, []);
  const deleteMessage = useCallback((withText: string) => {
    setMessages((prev) =>
      prev.filter((prevMessage) => prevMessage.text !== withText)
    );

    if (quote?.text === withText) {
      setQuote(null);
    }
  }, []);
  const quoteMessage = useCallback((message: ChatSpeakResponse) => {
    setQuote(message);

    try {
      document.getElementById("builtChatInput").focus();
    } catch (error) {}
  }, []);
  const context = useMemo<ChatProviderContext>(
    () => ({
      online,
      typing,
      messages,
      draft,
      quote,
      quoteMessage,
      sendMessage,
      deleteMessage: requestDeleteMessage,
      updateDraft: setDraft,
    }),
    [
      online,
      typing,
      messages,
      draft,
      quote,
      sendMessage,
      deleteMessage,
      quoteMessage,
    ]
  );

  useEffect(() => {
    if (!socket.current) {
      socket.current = io();

      socket.current
        .on(ChatHandlers.CATCHUP, setMessages)
        .on(ChatHandlers.ONLINE, setOnline)
        .on(ChatHandlers.TYPING, setTyping)
        .on(ChatHandlers.SPEAK, addMessage)
        .on(ChatHandlers.DELETE, deleteMessage);
    }
  });

  useEffect(() => {
    socket.current?.emit(ChatHandlers.TYPING, draft);
  }, [draft]);

  useEffect(() => {
    if (focused || document.hasFocus()) {
      setNotifications(0);
    }
  }, [focused]);

  // Display e.g. [+2] Chat when notifications occur when you're away.
  useEffect(() => {
    const title = document.getElementsByTagName("title")[0];
    const favicon = document.getElementById("favicon") as HTMLLinkElement;
    const escape = (window as any).escapeHTML;
    const alertedWhileAway = notifications > 0 && !focused;
    const pathIcon = alertedWhileAway ? "alert" : "icon";

    favicon.href = escape(`/assets/images/${siteName}/${pathIcon}.webp?v=3`);
    title.innerHTML = alertedWhileAway ? `[+${notifications}] Chat` : "Chat";
  }, [notifications, focused]);

  // Setup Lozad
  useEffect(() => {
    const { observe, observer } = lozad();

    observe();

    return () => {
      observer.disconnect();
    };
  }, []);

  return (
    <ChatContext.Provider value={context}>{children}</ChatContext.Provider>
  );
}

export function useChat() {
  const value = useContext(ChatContext);
  return value;
}
