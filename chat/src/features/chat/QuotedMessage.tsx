import React from "react";
import { useChat, useRootContext } from "../../hooks";
import { Username } from "./Username";
import "./QuotedMessage.css";
import { QuotedMessageLink } from "./QuotedMessageLink";

export function QuotedMessage() {
  const { quote, quoteMessage } = useChat();
  const { censored } = useRootContext();

  return (
    <div className="QuotedMessage">
      <QuotedMessageLink message={quote} />
      
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
