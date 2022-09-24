import React, { useCallback } from "react";
import { useChat, useDrawer } from "../../hooks";
import { UserList } from "./UserList";
import "./ChatHeading.css";

export function ChatHeading() {
  const { reveal } = useDrawer();
  const { online } = useChat();
  const handleOpenUserListDrawer = useCallback(
    () =>
      reveal({
        title: "Users in chat",
        content: <UserList fluid={true} />,
      }),
    []
  );

  return (
    <div className="ChatHeading">
      <div />
      <div>
        <i
          role="button"
          className="far fa-user"
          onClick={handleOpenUserListDrawer}
        />
        <em>{online.length} users online</em>
      </div>
    </div>
  );
}
