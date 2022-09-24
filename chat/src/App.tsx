import React, { useEffect, useRef } from "react";
import { DndProvider, useDrop } from "react-dnd";
import { HTML5Backend } from "react-dnd-html5-backend";
import {
  ChatHeading,
  ChatMessageList,
  QuotedMessage,
  UserInput,
  UserList,
  UsersTyping,
} from "./features";
import { ChatProvider, DrawerProvider, useChat, useDrawer } from "./hooks";
import "./App.css";

const SCROLL_CANCEL_THRESHOLD = 500;

export function App() {
  return (
    <DndProvider backend={HTML5Backend}>
      <DrawerProvider>
        <ChatProvider>
          <AppInner />
        </ChatProvider>
      </DrawerProvider>
    </DndProvider>
  );
}

function AppInner() {
  const [_, dropRef] = useDrop({
    accept: "drawer",
  });
  const { open, config } = useDrawer();
  const contentWrapper = useRef<HTMLDivElement>(null);
  const initiallyScrolledDown = useRef(false);
  const { messages, quote } = useChat();

  console.log({ quote });

  useEffect(() => {
    if (messages.length > 0) {
      if (initiallyScrolledDown.current) {
        /* We only want to scroll back down on a new message
         if the user is not scrolled up looking at previous messages. */
        const scrollableDistance =
          contentWrapper.current.scrollHeight -
          contentWrapper.current.clientHeight;
        const scrolledDistance = contentWrapper.current.scrollTop;
        const hasScrolledEnough =
          scrollableDistance - scrolledDistance >= SCROLL_CANCEL_THRESHOLD;

        if (hasScrolledEnough) {
          return;
        }
      } else {
        // Always scroll to the bottom on first load.
        initiallyScrolledDown.current = true;
      }

      contentWrapper.current.scrollTop = contentWrapper.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="App" ref={dropRef}>
      <div className="App-wrapper">
        <div className="App-heading">
          <small>v{process.env.VERSION}</small>
          <ChatHeading />
        </div>
        <div className="App-center">
          <div className="App-content" ref={contentWrapper}>
            {open ? (
              <div className="App-drawer">{config.content}</div>
            ) : (
              <ChatMessageList />
            )}
          </div>
          <div className="App-side">
            <UserList />
          </div>
        </div>
        <div className="App-bottom-wrapper">
          <div className="App-bottom">
            <div
              className="App-bottom-extra"
              style={{
                visibility: quote ? "visible" : "hidden",
              }}
            >
              {quote && <QuotedMessage />}
            </div>
            <UserInput />
            <UsersTyping />
          </div>
          <div className="App-bottom-dummy" />
        </div>
      </div>
    </div>
  );
}
