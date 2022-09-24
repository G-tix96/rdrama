import React, { useEffect, useRef } from "react";
import { Username } from "./Username";
import { useChat, useRootContext } from "../../hooks";
import "./ChatMessage.css";
import key from "weak-key";

interface ChatMessageProps extends ChatSpeakResponse {
  showUser?: boolean;
}

export function ChatMessage({
  avatar,
  showUser = true,
  namecolor,
  username,
  hat,
  text,
  text_html,
  text_censored,
  time,
  timestamp,
}: ChatMessageProps) {
  const message = {
    avatar,
    namecolor,
    username,
    hat,
    text,
    text_html,
    text_censored,
    time,
    timestamp,
  };
  const {
    username: loggedInUsername,
    admin,
    censored,
    themeColor,
  } = useRootContext();
  const { quote, deleteMessage, quoteMessage } = useChat();
  const content = censored ? text_censored : text_html;
  const hasMention = content.includes(loggedInUsername);
  const mentionStyle = hasMention
    ? { backgroundColor: `#${themeColor}55` }
    : {};
  const quoteStyle =
    quote?.username === username && quote?.text === text && quote?.time === time
      ? { borderLeft: `2px solid #${themeColor}` }
      : {};
  const style = { ...mentionStyle, ...quoteStyle };

  return (
    <div className={"ChatMessage"} style={style}>
      {showUser && (
        <div className="ChatMessage-top">
          <Username
            avatar={avatar}
            name={username}
            color={namecolor}
            hat={hat}
          />
          <div className="ChatMessage-timestamp">{timestamp}</div>
        </div>
      )}
      <div className="ChatMessage-bottom">
        <div>
          <span
            className="ChatMessage-content"
            title={content}
            dangerouslySetInnerHTML={{
              __html: content,
            }}
          />
          <button
            className="ChatMessage-button quote btn"
            onClick={() => quoteMessage(message)}
          >
            <i className="fas fa-reply"></i>
          </button>
        </div>
        {admin && (
          <button
            className="ChatMessage-button ChatMessage-delete quote btn del"
            onClick={() => deleteMessage(text)}
          >
            <i className="fas fa-trash-alt"></i>
          </button>
        )}
      </div>
    </div>
  );
}

export function ChatMessageList() {
  const { messages } = useChat();
  const scrolledOnce = useRef(false);
  const messageWrapper = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (messages.length > 0 && !scrolledOnce.current) {
      scrolledOnce.current = true;
      messageWrapper.current.scrollTop = messageWrapper.current?.scrollHeight;
    }
  }, [messages])

  return (
    <div className="ChatMessageList" ref={messageWrapper}>
      {messages.map((message, index) => (
        <ChatMessage
          key={key(message)}
          {...message}
          showUser={message.username !== messages[index - 1]?.username}
        />
      ))}
    </div>
  );
}
