import React from "react";
import { useChat, useDrawer } from "../../hooks";
import { ActivityList } from "./ActivityList";
import { ChatMessageList } from "./ChatMessage";
import { QuotedMessage } from "./QuotedMessage";
import { UserInput } from "./UserInput";
import { UserList } from "./UserList";
import "./Chat.css";

export function Chat() {
  const { reveal } = useDrawer();
  const { online, quote } = useChat();

  return (
    <section className="Chat" id="chatWrapper">
      <div className="Chat-window">
        <div className="Chat-mobile-top">
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() =>
              reveal({
                title: "Users in chat",
                content: (
                  <div className="Chat-drawer">
                    <UserList fluid={true} />
                  </div>
                ),
              })
            }
          >
            <i className="far fa-user" /> <span>{online.length}</span>
          </button>
        </div>
        <ChatMessageList />
        {quote && <QuotedMessage />}
        <UserInput />
      </div>
      <div className="Chat-side">
        <UserList />
        {process.env.FEATURES_ACTIVITY && <ActivityList />}
      </div>
    </section>
  );
}