import React from "react";
import { DndProvider, useDrop } from "react-dnd";
import { HTML5Backend } from "react-dnd-html5-backend";
import {
  ChatHeading,
  ChatMessageList,
  UserInput,
  UserList,
  UsersTyping,
} from "./features";
import { ChatProvider, DrawerProvider, useDrawer } from "./hooks";
import "./App.css";

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

  return (
    <div className="App" ref={dropRef}>
      <div className="App-wrapper">
        <div className="App-heading">
          <small>v{process.env.VERSION}</small>
          <ChatHeading />
        </div>
        <div id="chatWrapper" className="App-content">
          <div style={{ flex: 1 }}>
            {open && config.content ? (
              <div className="App-drawer">{config.content}</div>
            ) : (
              <ChatMessageList />
            )}
          </div>
          <div className="App-side">
            <UserList />
          </div>
        </div>
        <div className="App-input">
          <UserInput />
          <UsersTyping />
        </div>
      </div>
    </div>
  );
}
