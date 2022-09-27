import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import debounce from "lodash.debounce";

const FAVORITES_STORAGE_KEY = "Emojis/Favorites";
const MINIMUM_SEARCH_INTERVAL = 350;

interface MarseyListEmoji {
  author: string;
  class: string;
  count: number;
  name: string;
  tags: string[];
}

export function useEmojis() {
  const emojiDictionary = useRef(new EmojiDictionary());
  const [error, setError] = useState("");
  const [emojis, setEmojis] = useState<MarseyListEmoji[]>([]);
  const [genres, setGenres] = useState<string[]>([]);
  const [collections, setCollections] = useState<Record<string, string[]>>({});
  const [favorites, setFavorites] = useState<string[]>([]);
  const [queries, setQueries] = useState<string[]>([]);
  const [mostRecentQuery, setMostRecentQuery] = useState("");
  const [visible, setVisible] = useState<string[]>([]);
  const addQuery = useCallback(
    (query: string) => setQueries((prev) => prev.concat(query)),
    []
  );
  const debouncedQueryAdder = useMemo(
    () => debounce(addQuery, MINIMUM_SEARCH_INTERVAL),
    []
  );

  // Retrieve the list.
  useEffect(() => {
    fetch("/marsey_list.json")
      .then((res) => res.json())
      .then(setEmojis)
      .catch(setError);
  }, []);

  // Load favorites.
  useEffect(() => {
    const persisted = window.localStorage.getItem(FAVORITES_STORAGE_KEY);

    if (persisted) {
      setFavorites(JSON.parse(persisted));
    }
  }, []);

  // Persist favorites.
  useEffect(() => {
    window.localStorage.setItem(
      FAVORITES_STORAGE_KEY,
      JSON.stringify(Array.from(new Set(favorites)))
    );
  }, [favorites]);

  // When emojis are received, update the dictionary.
  useEffect(() => {
    const dictionary = emojiDictionary.current;
    const genreCollections: Record<string, string[]> = {};

    for (const emoji of emojis) {
      dictionary.updateTag(emoji.name, emoji.name);

      if (typeof emoji.author !== "undefined" && emoji.author !== null) {
        dictionary.updateTag(emoji.author.toLowerCase(), emoji.name);
      }

      if (emoji.tags instanceof Array) {
        for (const tag of emoji.tags) {
          dictionary.updateTag(tag, emoji.name);
        }
      }

      dictionary.classes.add(emoji.class);

      if (!genreCollections[emoji.class]) {
        genreCollections[emoji.class] = [];
      }

      genreCollections[emoji.class].push(emoji.name);
    }

    setGenres(Array.from(dictionary.classes.values()) as string[]);
    setCollections(genreCollections);
  }, [emojis]);

  // Process queries as they come in.
  useEffect(() => {
    if (queries.length > 0) {
      const lastQuery = queries[queries.length - 1].toLowerCase();

      setQueries([]);
      setMostRecentQuery(lastQuery);

      if (lastQuery.length === 0) {
        return setVisible([]);
      }

      const results = emojiDictionary.current.completeSearch(lastQuery);
      const nextVisible = Array.from(results.values()) as string[];

      setVisible(nextVisible);
    }
  }, [queries]);

  // Clean up any debounced calls before exit.
  useEffect(() => {
    return () => {
      debouncedQueryAdder.cancel();
    };
  }, []);

  return {
    error,
    ready: emojis.length > 0,
    visible,
    genres,
    collections,
    favorites,
    mostRecentQuery,
    addQuery,
    updateVisible: setVisible,
    updateFavorites: setFavorites
  };
}

class EmojiDictionaryNode {
  tag = "";
  names = [];

  constructor(tag: string, name: string) {
    this.tag = tag;
    this.names = [name];
  }
}

class EmojiDictionary {
  dictionary = [];
  classes = new Set();

  updateTag(tag: string, name: string) {
    let low = 0;
    let high = this.dictionary.length;

    while (low < high) {
      let mid = (low + high) >>> 1;

      if (this.dictionary[mid].tag.length < tag.length) {
        low = mid + 1;
      } else {
        high = mid;
      }
    }

    let target = low;

    if (
      typeof this.dictionary[target] !== "undefined" &&
      this.dictionary[target].tag === tag
    ) {
      this.dictionary[target].names.push(name);
    } else {
      this.dictionary.splice(target, 0, new EmojiDictionaryNode(tag, name));
    }
  }

  searchFor(query: string) {
    query = query.toLowerCase();
    const result = new Set();

    if (this.dictionary.length === 0) {
      return result;
    }

    let low = 0;
    let high = this.dictionary.length;

    while (low < high) {
      let mid = (low + high) >>> 1;

      if (this.dictionary[mid].tag.length < query.length) {
        low = mid + 1;
      } else {
        high = mid;
      }
    }

    let target = low;

    for (
      let i = target;
      i >= 0 && this.dictionary[i].tag.startsWith(query);
      i--
    ) {
      for (const name of this.dictionary[i].names) {
        result.add(name);
      }
    }

    for (
      let i = target + 1;
      i < this.dictionary.length && this.dictionary[i].tag.startsWith(query);
      i++
    ) {
      for (const name of this.dictionary[i].names) {
        result.add(name);
      }
    }

    return result;
  }

  completeSearch(query: string) {
    query = query.toLowerCase();
    const result = new Set();

    for (const { tag, names } of this.dictionary) {
      if (tag.includes(query)) {
        for (const name of names) {
          result.add(name);
        }
      }
    }

    return result;
  }
}
