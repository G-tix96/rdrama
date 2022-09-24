import React, {
  useRef,
  useMemo,
  useCallback,
  useEffect,
  useState,
} from "react";
import { FixedSizeGrid, FixedSizeGrid as Grid } from "react-window";
import AutoSizer from "react-virtualized-auto-sizer";
import { useDrawer, useEmojis } from "../../hooks";
import { BaseDrawer } from "../../drawers";
import { EmojiGenres } from "./EmojiGenres";
import { EmojiMods } from "./EmojiMods";
import "./EmojiDrawer.css";

interface Props {
  onSelectEmoji(emoji: string): void;
  onClose?(): void;
}

enum EmojiDrawerTabs {
  Favorites = "Favorites",
}

export function EmojiDrawer({ onSelectEmoji, onClose }: Props) {
  const {
    visible,
    genres,
    collections,
    favorites,
    mostRecentQuery,
    addQuery,
    updateVisible,
    updateFavorites,
  } = useEmojis();
  const { hide } = useDrawer();
  const [modSelection, setModSelection] = useState<EmojiModSelection>({
    large: false,
    mirror: false,
    pat: false,
  });
  const [activeGenre, setActiveGenre] = useState<string>(
    EmojiDrawerTabs.Favorites
  );
  const emojiGrid = useMemo(() => {
    const grid = [];
    let temp = [];

    for (let i = 0; i < visible.length; i++) {
      temp.push(visible[i]);

      if (i % 7 === 0) {
        grid.push([...temp]);
        temp = [];
      }
    }

    return grid;
  }, [visible]);

  // Refs
  const gridRef = useRef<FixedSizeGrid<any>>();
  const input = useRef<HTMLInputElement>(null);

  // Callbacks
  const handleEmojiGenreChange =
    /*useCallback(*/
    (genre: string) => {
      setActiveGenre(genre);

      if (genre === EmojiDrawerTabs.Favorites) {
        updateVisible(favorites);
      } else {
        updateVisible(collections[genre] ?? []);
      }
    };
  /*[favorites, collections]
  );*/
  const handleScrollToTop = useCallback(() => {
    gridRef.current?.scrollToItem({
      rowIndex: 0,
    });
  }, []);
  const handleSelectEmoji = useCallback(
    (emoji: string) => {
      if (modSelection.large) {
        emoji = `#${emoji}`;
      }

      if (modSelection.mirror) {
        emoji = `!${emoji}`;
      }

      if (modSelection.pat) {
        emoji = `${emoji}pat`;
      }

      onSelectEmoji(emoji);
      updateFavorites((prev) => Array.from(new Set(prev.concat(emoji))));
    },
    [modSelection]
  );
  const handleClose = useCallback(() => {
    hide();
    onClose();
  }, [onClose]);

  // Effects
  // When the user types more, scroll back up.
  useEffect(() => {
    handleScrollToTop();
  }, [visible]);

  // Enter and Esc finish the interaction.
  useEffect(() => {
    const handleKeyup = (event: KeyboardEvent) => {
      if (["Escape", "Enter"].includes(event.key)) {
        handleClose();
      }
    };

    document.addEventListener("keyup", handleKeyup);

    return () => {
      document.removeEventListener("keyup", handleKeyup);
    };
  }, [handleClose]);

  // Cell
  const Cell = useCallback(
    ({ columnIndex, rowIndex, style }) => {
      const emoji = emojiGrid[rowIndex]?.[columnIndex];

      return emoji ? (
        <img
          role="button"
          onClick={() => handleSelectEmoji(emoji)}
          style={{
            ...style,
            cursor: "pointer",
            margin: "1rem",
          }}
          loading="lazy"
          width={60}
          src={`/e/${emoji}.webp`}
          alt={emoji}
        />
      ) : null;
    },
    [emojiGrid, handleSelectEmoji]
  );

  return (
    <BaseDrawer onClose={handleClose}>
      <div className="EmojiDrawer-input">
        <input
          ref={input}
          className="form-control"
          type="text"
          onChange={(e) => addQuery(e.target.value)}
          autoFocus={true}
          placeholder="Search for emojis..."
          style={{
            margin: "1rem",
            flex: 1,
          }}
        />
      </div>
      <div className="EmojiDrawer-options">
        <EmojiMods
          selection={modSelection}
          onChangeSelection={setModSelection}
        />
        <EmojiGenres
          genres={genres}
          activeGenre={activeGenre}
          onGenreChange={handleEmojiGenreChange}
        />
      </div>
      {/* Results */}
      {visible.length > 0 && (
        <AutoSizer>
          {({ width, height }) => (
            <Grid
              ref={gridRef}
              columnCount={8}
              columnWidth={64}
              rowCount={visible.length}
              rowHeight={64}
              width={width}
              height={height}
            >
              {Cell}
            </Grid>
          )}
        </AutoSizer>
      )}
      {/* Searched, nothing found */}
      {visible.length === 0 && mostRecentQuery !== "" && (
        <div>Nothing found.</div>
      )}
      {/* Favorites */}
      {visible.length === 0 &&
        mostRecentQuery === "" &&
        favorites.map((favorite) => (
          <img
            key={favorite}
            role="button"
            onClick={() => handleSelectEmoji(favorite)}
            style={{
              cursor: "pointer",
              margin: "1rem",
            }}
            loading="lazy"
            width={60}
            src={`/e/${favorite}.webp`}
            alt={favorite}
          />
        ))}
    </BaseDrawer>
  );
}
