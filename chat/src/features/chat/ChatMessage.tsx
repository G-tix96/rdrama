import React, { useCallback, useEffect, useMemo, useState } from "react";
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
  const { admin, censored } = useRootContext();
  const { messageLookup, deleteMessage, quoteMessage } = useChat();
  const quotedMessage = messageLookup[quotes];
  const content = censored ? text_censored : text_html;
  const [showingActions, setShowingActions] = useState(false);
  const [confirmedDelete, setConfirmedDelete] = useState(false);
  const timestamp = useMemo(
    () => formatTimeAgo(time),
    [time, timestampUpdates]
  );
  const handleDeleteMessage = useCallback(() => {
    if (confirmedDelete) {
      deleteMessage(text);
    } else {
      setConfirmedDelete(true);
    }
  }, [text, confirmedDelete]);
  const toggleMessageActions = useCallback(
    () => setShowingActions((prev) => !prev),
    []
  );
  const handleQuoteMessage = useCallback(() => {
    quoteMessage(message);
    setShowingActions(false);
  }, [message]);

  useEffect(() => {
    if (!showingActions) {
      setConfirmedDelete(false);
    }
  }, [showingActions]);

  return (
    <div
      className={cx("ChatMessage", {
        ChatMessage__showingUser: showUser,
      })}
      id={id}
    >
      {!showingActions && (
        <button
          className="btn btn-secondary ChatMessage-actions-button"
          onClick={toggleMessageActions}
        >
          ...
        </button>
      )}
      {showingActions && (
        <div className="ChatMessage-actions">
          <button
            className="btn btn-secondary ChatMessage-button"
            onClick={handleQuoteMessage}
          >
            <i className="fas fa-reply" /> Reply
          </button>
          {admin && (
            <button
              className={cx("btn btn-secondary ChatMessage-button", {
                "ChatMessage-button__confirmed": confirmedDelete,
              })}
              onClick={handleDeleteMessage}
            >
              <i className="fas fa-trash-alt" />{" "}
              {confirmedDelete ? "Are you sure?" : "Delete"}
            </button>
          )}
          <button
            className="btn btn-secondary ChatMessage-button"
            onClick={toggleMessageActions}
          >
            <i>X</i> Close
          </button>
        </div>
      )}
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
        </div>
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
  const shortEnglishHumanizer = humanizeDuration.humanizer({
    language: "shortEn",
    languages: {
      shortEn: {
        y: () => "y",
        mo: () => "mo",
        w: () => "w",
        d: () => "d",
        h: () => "h",
        m: () => "m",
        s: () => "s",
        ms: () => "ms",
      },
    },
    round: true,
    units: ["h", "m", "s"],
    largest: 2,
    spacer: "",
    delimiter: ", ",
  });
  const now = new Date().getTime();
  const humanized = `${shortEnglishHumanizer(time * 1000 - now)} ago`;

  return humanized === "0s ago" ? "just now" : humanized;
}
