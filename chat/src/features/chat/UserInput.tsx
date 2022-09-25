import React, {
  ChangeEvent,
  KeyboardEvent,
  FormEvent,
  useCallback,
  useRef,
  useMemo,
  useState,
} from "react";
import { useChat, useDrawer, useEmojis } from "../../hooks";
import { EmojiDrawer, QuickEmojis } from "../emoji";
import "./UserInput.css";

export function UserInput() {
  const { draft, sendMessage, updateDraft } = useChat();
  const { reveal, hide, open } = useDrawer();
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
      if (event.key === "Enter") {
        handleSendMessage();
      }
    },
    [handleSendMessage]
  );
  const handleToggleEmojiDrawer = useCallback(() => {
    if (open) {
      builtChatInput.current?.focus();
      hide();
    } else {
      reveal({
        title: "Select an emoji",
        content: (
          <EmojiDrawer
            onSelectEmoji={handleSelectEmoji}
            onClose={() => builtChatInput.current?.focus()}
          />
        ),
      });
    }
  }, [open]);
  const handleSelectEmoji = useCallback((emoji: string) => {
    updateDraft((prev) => `${prev} :${emoji}: `);
  }, []);
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
        className="UserInput-input form-control"
        style={{
          minHeight: 50,
          height: 50,
          maxHeight: 50,
        }}
        minLength={1}
        maxLength={1000}
        rows={1}
        onChange={handleChange}
        onKeyUp={handleKeyUp}
        placeholder="Message"
        autoComplete="off"
        value={draft}
      />
      <i
        role="button"
        onClick={handleToggleEmojiDrawer}
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
