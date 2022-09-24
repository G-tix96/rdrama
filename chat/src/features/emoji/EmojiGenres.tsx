import React, { ChangeEvent, useCallback } from "react";
import "./EmojiGenres.css";

interface Props {
  genres: string[];
  activeGenre: string;
  onGenreChange(genre: string): void;
}

export function EmojiGenres({ genres, activeGenre, onGenreChange }: Props) {
  const handleSelect = useCallback((event: ChangeEvent<HTMLSelectElement>) => {
    onGenreChange(event.target.value);
  }, [onGenreChange]);

  return (
    <select onChange={handleSelect} value={activeGenre}>
      <option value="Favorites">⭐ Favorites ⭐</option>
      {genres.map((genre) => (
        <option key={genre} value={genre}>
          {genre}
        </option>
      ))}
    </select>
  );
}
