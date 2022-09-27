import React, {
  ChangeEvent,
  KeyboardEvent,
  FormEvent,
  useCallback,
  useRef,
  useMemo,
  useState,
  useEffect,
} from "react";
import cx from "classnames";
import { useChat, useEmojis } from "../../hooks";
import { QuickEmojis } from "../emoji";
import "./UserInput.css";

interface Props {
  large?: boolean;
  onFocus(): void;
  onBlur(): void;
}

export function UserInput({ large = false, onFocus, onBlur }: Props) {
  const { draft, userToDm, sendMessage, updateDraft } = useChat();
  const builtChatInput = useRef<HTMLTextAreaElement>(null);
  const { visible, addQuery } = useEmojis();
  const form = useRef<HTMLFormElement>(null);
  const [typingOffset, setTypingOffset] = useState(0);
  const quickEmojis = useMemo(
    () => visible.slice(0, process.env.QUICK_EMOJIS_MAX_COUNT),
    [visible]
  );
  const handleChange = useCallback(
    (event: ChangeEvent<HTMLTextAreaElement>) => {
      const input = event.target.value;
      const [openEmojiToken, closeEmojiToken] = locateEmojiTokens(input);
      const emojiSegment = input.slice(openEmojiToken + 1, closeEmojiToken + 1);

      updateDraft(input);
      addQuery(
        openEmojiToken === -1 || emojiSegment.includes(" ") ? "" : emojiSegment
      );
      setTypingOffset(
        emojiSegment.length * process.env.APPROXIMATE_CHARACTER_WIDTH
      );
    },
    []
  );
  const handleSendMessage = useCallback(
    (event?: FormEvent<HTMLFormElement>) => {
      event?.preventDefault();
      sendMessage();
    },
    [sendMessage]
  );
  const handleKeyUp = useCallback(
    (event: KeyboardEvent<HTMLTextAreaElement>) => {
      if (event.key === "Enter" && !event.shiftKey) {
        handleSendMessage();
      }
    },
    [handleSendMessage]
  );
  const handleInsertQuickEmoji = useCallback(
    (emoji: string) => {
      const [openEmojiToken, closeEmojiToken] = locateEmojiTokens(draft);
      const toReplace = draft.slice(openEmojiToken, closeEmojiToken + 1);

      updateDraft((prev) => prev.replace(toReplace, `:${emoji}: `));
      addQuery("");

      builtChatInput.current?.focus();
    },
    [draft]
  );
  const handleFocus = useCallback(() => {
    builtChatInput.current?.scrollIntoView({ behavior: "smooth" });
    onFocus();
  }, [onFocus]);

  // Listen for changes from the Emoji Modal and reflect them in draft
  useEffect(() => {
    const handleEmojiInsert = (event: CustomEvent<{ emoji: string }>) =>
      updateDraft((prev) => `${prev} ${event.detail.emoji} `);

    document.addEventListener("emojiInserted", handleEmojiInsert);

    return () => {
      document.removeEventListener("emojiInserted", handleEmojiInsert);
    }
  }, []);

  useEffect(() => {
    if (userToDm) {
      builtChatInput.current?.focus();
    }
  }, [userToDm])

  return (
    <form ref={form} className="UserInput" onSubmit={handleSendMessage}>
      {quickEmojis.length > 0 && (
        <div
          style={{
            position: "absolute",
            top: -254,
            height: 250,
            left: typingOffset,
            display: "flex",
            flexDirection: "column-reverse",
          }}
        >
          <QuickEmojis
            emojis={quickEmojis}
            onSelectEmoji={handleInsertQuickEmoji}
          />
        </div>
      )}
      <textarea
        ref={builtChatInput}
        id="builtChatInput"
        className={cx("UserInput-input form-control", {
          "UserInput-input__large": large
        })}
        minLength={1}
        maxLength={1000}
        rows={1}
        onChange={handleChange}
        onKeyUp={handleKeyUp}
        onFocus={handleFocus}
        onBlur={onBlur}
        placeholder="Message"
        autoComplete="off"
        value={draft}
      />
      <i
        role="button"
        data-bs-toggle="modal"
        data-bs-target="#emojiModal"
        data-bs-placement="bottom"
        title="Add Emoji"
        onClick={() => {
          const whatever = window as any;
          whatever.loadEmojis("builtChatInput");
        }}
        className="UserInput-emoji fas fa-smile-beam"
      />
      <button
        className="btn btn-secondary"
        disabled={draft.length === 0}
        onClick={sendMessage}
      >
        <i className="UserInput-emoji fas fa-reply" />
      </button>
    </form>
  );
}

function locateEmojiTokens(text: string) {
  let openEmojiInputToken = -1;
  let endEmojiInputToken = -1;

  if (text.length <= 1) {
    return [openEmojiInputToken, endEmojiInputToken];
  }

  for (let i = 0; i < text.length; i++) {
    const character = text[i];

    if (character === process.env.EMOJI_INPUT_TOKEN) {
      if (openEmojiInputToken === -1) {
        openEmojiInputToken = i;
      } else {
        openEmojiInputToken = -1;
      }
    }
  }

  if (openEmojiInputToken !== -1) {
    endEmojiInputToken = openEmojiInputToken;

    while (
      endEmojiInputToken < text.length - 1 &&
      text[endEmojiInputToken] !== " "
    ) {
      endEmojiInputToken++;
    }
  }

  return [openEmojiInputToken, endEmojiInputToken];
}
