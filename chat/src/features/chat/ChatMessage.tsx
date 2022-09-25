import React, { useCallback, useEffect, useMemo, useState } from "react";
import cx from "classnames";
import key from "weak-key";
import humanizeDuration from "humanize-duration";
import cloneDeep from "lodash.clonedeep";
import { Username } from "./Username";
import { useChat, useRootContext } from "../../hooks";
import { QuotedMessageLink } from "./QuotedMessageLink";
import "./ChatMessage.css";

interface ChatMessageProps {
  message: IChatMessage;
  timestampUpdates: number;
  showUser?: boolean;
  actionsOpen: boolean;
  onToggleActions(messageId: string): void;
}

const TIMESTAMP_UPDATE_INTERVAL = 20000;

export function ChatMessage({
  message,
  showUser = true,
  timestampUpdates,
  actionsOpen,
  onToggleActions,
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
  const handleQuoteMessageAction = useCallback(() => {
    quoteMessage(message);
    onToggleActions(message.id);
  }, [message, onToggleActions]);

  useEffect(() => {
    if (!actionsOpen) {
      setConfirmedDelete(false);
    }
  }, [actionsOpen]);

  return (
    <div
      className={cx("ChatMessage", {
        ChatMessage__showingUser: showUser,
      })}
      id={id}
    >
      {!actionsOpen && (
        <div className="ChatMessage-actions-button">
          <button
            className="btn btn-secondary"
            onClick={() => quoteMessage(message)}
          >
            <i className="fas fa-reply" />
          </button>
          <button
            className="btn btn-secondary"
            onClick={() => onToggleActions(id)}
          >
            ...
          </button>
        </div>
      )}
      {actionsOpen && (
        <div className="ChatMessage-actions">
          <button
            className="btn btn-secondary ChatMessage-button"
            onClick={handleQuoteMessageAction}
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
            onClick={() => onToggleActions(id)}
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
  const groupedMessages = useMemo(() => groupMessages(messages), [messages]);
  const [actionsOpenForMessage, setActionsOpenForMessage] = useState<
    string | null
  >(null);
  const handleToggleActionsForMessage = useCallback(
    (messageId: string) =>
      setActionsOpenForMessage(
        messageId === actionsOpenForMessage ? null : messageId
      ),
    [actionsOpenForMessage]
  );

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
      {groupedMessages.map((group) => (
        <div key={key(group)} className="ChatMessageList-group">
          {group.map((message, index) => (
            <ChatMessage
              key={key(message)}
              message={message}
              timestampUpdates={timestampUpdates}
              showUser={index === 0}
              actionsOpen={actionsOpenForMessage === message.id}
              onToggleActions={handleToggleActionsForMessage}
            />
          ))}
        </div>
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

function groupMessages(messages: IChatMessage[]) {
  const grouped: IChatMessage[][] = [];
  let lastUsername = "";
  let temp: IChatMessage[] = [];

  for (const message of messages) {
    if (!lastUsername) {
      lastUsername = message.username;
    }

    if (message.username === lastUsername) {
      temp.push(message);
    } else {
      grouped.push(cloneDeep(temp));
      lastUsername = message.username;
      temp = [message];
    }
  }

  if (temp.length > 0) {
    grouped.push(cloneDeep(temp));
  }

  return grouped;
}
