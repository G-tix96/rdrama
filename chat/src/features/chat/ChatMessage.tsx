import React, {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";
import cx from "classnames";
import key from "weak-key";
import humanizeDuration from "humanize-duration";
import { Username } from "./Username";
import { useChat, useRootContext } from "../../hooks";
import { QuotedMessageLink } from "./QuotedMessageLink";
import "./ChatMessage.css";

interface ChatMessageProps {
  message: IChatMessage;
  timestampUpdates: number;
  showUser?: boolean;
}

const TIMESTAMP_UPDATE_INTERVAL = 20000;

export function ChatMessage({
  message,
  showUser = true,
  timestampUpdates,
}: ChatMessageProps) {
  const {
    id,
    avatar,
    namecolor,
    username,
    hat,
    text,
    text_html,
    text_censored,
    time,
    quotes,
  } = message;
  const {
    username: loggedInUsername,
    admin,
    censored,
    themeColor,
  } = useRootContext();
  const { messageLookup, deleteMessage, quoteMessage } = useChat();
  const quotedMessage = messageLookup[quotes];
  const content = censored ? text_censored : text_html;
  const hasMention = content.includes(loggedInUsername);
  const mentionStyle = hasMention
    ? { backgroundColor: `#${themeColor}55` }
    : {};
  const [confirmedDelete, setConfirmedDelete] = useState(false);
  const handleDeleteMessage = useCallback(() => {
    if (confirmedDelete) {
      deleteMessage(text);
    } else {
      setConfirmedDelete(true);
    }
  }, [text, confirmedDelete]);
  const timestamp = useMemo(
    () => formatTimeAgo(time),
    [time, timestampUpdates]
  );

  return (
    <div className="ChatMessage" style={mentionStyle} id={id}>
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
      {quotes && quotedMessage && <QuotedMessageLink message={quotedMessage} />}
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
            className={cx("ChatMessage-button ChatMessage-delete btn", {
              "ChatMessage-button__confirmed": confirmedDelete,
            })}
            onClick={handleDeleteMessage}
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
  const [timestampUpdates, setTimestampUpdates] = useState(0);

  useEffect(() => {
    const updatingTimestamps = setInterval(
      () => setTimestampUpdates((prev) => prev + 1),
      TIMESTAMP_UPDATE_INTERVAL
    );

    return () => {
      clearInterval(updatingTimestamps);
    };
  }, []);

  return (
    <div className="ChatMessageList">
      {messages.map((message, index) => (
        <ChatMessage
          key={key(message)}
          message={message}
          timestampUpdates={timestampUpdates}
          showUser={message.username !== messages[index - 1]?.username}
        />
      ))}
    </div>
  );
}

function formatTimeAgo(time: number) {
  const now = new Date().getTime();
  const humanized = `${humanizeDuration(time * 1000 - now, {
    round: true,
    units: ["h", "m", "s"],
    largest: 2,
  })} ago`;

  return humanized === "0 seconds ago" ? "just now" : humanized;
}
