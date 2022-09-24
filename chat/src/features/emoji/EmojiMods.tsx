import React, { useCallback, useRef } from "react";

interface Props {
  selection: EmojiModSelection;
  onChangeSelection(selection: EmojiModSelection): void;
}

export function EmojiMods({ selection, onChangeSelection }: Props) {
  const largeOption = useRef<HTMLInputElement>(null);
  const mirrorOption = useRef<HTMLInputElement>(null);
  const patOption = useRef<HTMLInputElement>(null);
  const handleChangeSelection = useCallback(() => {
    onChangeSelection({
      large: largeOption.current.checked,
      mirror: mirrorOption.current.checked,
      pat: patOption.current.checked,
    });
  }, []);

  return (
    <div className="EmojiMods">
      <input
        type="checkbox"
        id="largeOption"
        ref={largeOption}
        onChange={handleChangeSelection}
        checked={selection.large}
        style={{ marginLeft: "1rem", marginRight: "0.5rem" }}
      ></input>
      <label htmlFor="largeOption" style={{ marginRight: "1rem" }}>
        Large
      </label>
      <input
        type="checkbox"
        id="mirrorOption"
        ref={mirrorOption}
        onChange={handleChangeSelection}
        checked={selection.mirror}
        style={{ marginRight: "0.5rem" }}
      ></input>
      <label htmlFor="mirrorOption" style={{ marginRight: "1rem" }}>
        Mirror
      </label>
      <input
        type="checkbox"
        id="patOption"
        ref={patOption}
        onChange={handleChangeSelection}
        checked={selection.pat}
        style={{ marginRight: "0.5rem" }}
      ></input>
      <label htmlFor="patOption">Pat</label>
    </div>
  );
}
