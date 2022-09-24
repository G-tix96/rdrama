import React from "react";
import { useChat, useRootContext } from "../../hooks";
import { Username } from "./Username";
import "./QuotedMessage.css";

export function QuotedMessage() {
  const { quote, quoteMessage } = useChat();
  const { censored } = useRootContext();

  return (
    <div className="QuotedMessage">
      <div>
        <Username
          avatar={quote.avatar}
          color={quote.namecolor}
          name={quote.username}
          hat={quote.hat}
        />
      </div>
      <div
        className="QuotedMessage-content"
        dangerouslySetInnerHTML={{
          __html: censored ? quote.text_censored : quote.text_html,
        }}
      />
      <button
        type="button"
        className="btn btn-secondary"
        onClick={() => quoteMessage(null)}
      >
        Cancel
      </button>
    </div>
  );
}
