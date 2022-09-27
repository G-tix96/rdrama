import React from "react";

interface Props {
  emojis: string[];
  onSelectEmoji(emoji: string): void;
}

export function QuickEmojis({ emojis, onSelectEmoji }: Props) {
  return (
    <div
      style={{
        backgroundColor: "var(--gray-700)",
        maxHeight: 250,
        overflowY: "auto",
        overflowX: "hidden",
        borderRadius: "4px",
        border: "1px solid rgba(255, 255, 255, 0.3)",
        boxShadow: "0px 2px 5px rgb(0 0 0 / 20%)",
        zIndex: 999,
      }}
    >
      {emojis.map((emoji) => (
        <div
          key={emoji}
          role="button"
          onClick={() => onSelectEmoji(emoji)}
          style={{
            borderBottom: "1px solid #606060",
            padding: "4px",
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <img
            src={`/e/${emoji}.webp`}
            style={{
              objectFit: "contain",
              width: 30,
              height: 30,
            }}
          />
          <span>{emoji}</span>
        </div>
      ))}
    </div>
  );
}
