import React, { useCallback } from "react";
import { useRootContext } from "../../hooks";

const SCROLL_TO_QUOTED_OVERFLOW = 250;
const QUOTED_MESSAGE_CONTEXTUAL_HIGHLIGHTING_DURATION = 2500;
const QUOTED_MESSAGE_CONTEXTUAL_SNIPPET_LENGTH = 30;

export function QuotedMessageLink({ message }: { message: IChatMessage }) {
  const { themeColor } = useRootContext();
  const handleLinkClick = useCallback(() => {
    const element = document.getElementById(message.id);

    if (element) {
      element.scrollIntoView();
      element.style.background = `#${themeColor}33`;

      setTimeout(() => {
        element.style.background = "unset";
      }, QUOTED_MESSAGE_CONTEXTUAL_HIGHLIGHTING_DURATION);

      const [appContent] = Array.from(
        document.getElementsByClassName("App-content")
      );

      if (appContent) {
        appContent.scrollTop -= SCROLL_TO_QUOTED_OVERFLOW;
      }
    }
  }, []);

  return (
    <a href="#" onClick={handleLinkClick}>
      Replying to @{message.username}:{" "}
      <em>
        "{message.text.slice(0, QUOTED_MESSAGE_CONTEXTUAL_SNIPPET_LENGTH)}
        {message.text.length >= QUOTED_MESSAGE_CONTEXTUAL_SNIPPET_LENGTH
          ? "..."
          : ""}
        "
      </em>
    </a>
  );
}
