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
import debounce from "lodash.debounce";
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
  messages: IChatMessage[];
  draft: string;
  quote: null | IChatMessage;
  messageLookup: Record<string, IChatMessage>;
  updateDraft: React.Dispatch<React.SetStateAction<string>>;
  sendMessage(): void;
  quoteMessage(message: null | IChatMessage): void;
  deleteMessage(withText: string): void;
}

const ChatContext = createContext<ChatProviderContext>({
  online: [],
  typing: [],
  messages: [],
  draft: "",
  quote: null,
  messageLookup: {},
  updateDraft() {},
  sendMessage() {},
  quoteMessage() {},
  deleteMessage() {},
});

const MINIMUM_TYPING_UPDATE_INTERVAL = 250;

export function ChatProvider({ children }: PropsWithChildren) {
  const { username, siteName } = useRootContext();
  const socket = useRef<null | Socket>(null);
  const [online, setOnline] = useState<string[]>([]);
  const [typing, setTyping] = useState<string[]>([]);
  const [messages, setMessages] = useState<IChatMessage[]>([]);
  const [draft, setDraft] = useState("");
  const lastDraft = useRef("");
  const [quote, setQuote] = useState<null | IChatMessage>(null);
  const focused = useWindowFocus();
  const [notifications, setNotifications] = useState<number>(0);
  const [messageLookup, setMessageLookup] = useState({});
  const addMessage = useCallback((message: IChatMessage) => {
    setMessages((prev) => prev.concat(message));

    if (message.username !== username && !document.hasFocus()) {
      setNotifications((prev) => prev + 1);
    }
  }, []);
  const sendMessage = useCallback(() => {
    socket.current?.emit(ChatHandlers.SPEAK, {
      message: draft,
      quotes: quote?.id ?? null,
    });

    setQuote(null);
    setDraft("");
  }, [draft, quote]);
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
  const quoteMessage = useCallback((message: IChatMessage) => {
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
      messageLookup,
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
      messageLookup,
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

  const debouncedTypingUpdater = useMemo(
    () =>
      debounce(
        () => socket.current?.emit(ChatHandlers.TYPING, lastDraft.current),
        MINIMUM_TYPING_UPDATE_INTERVAL
      ),
    []
  );

  useEffect(() => {
    lastDraft.current = draft;
    debouncedTypingUpdater();
  }, [draft]);

  useEffect(() => {
    if (focused || document.hasFocus()) {
      setNotifications(0);
    }
  }, [focused]);

  useEffect(() => {
    setMessageLookup(
      messages.reduce((prev, next) => {
        prev[next.id] = next;
        return prev;
      }, {} as Record<string, IChatMessage>)
    );
  }, [messages]);

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

  return (
    <ChatContext.Provider value={context}>{children}</ChatContext.Provider>
  );
}

export function useChat() {
  const value = useContext(ChatContext);
  return value;
}
