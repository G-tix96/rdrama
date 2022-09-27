declare var process: {
  env: Record<string, any>;
};

declare interface IChatMessage {
  id: string;
  username: string;
  user_id?: string;
  avatar: string;
  hat: string;
  namecolor: string;
  text: string;
  base_text_censored: string;
  text_censored: string;
  text_html: string;
  time: number;
  quotes: null | string;
  dm: boolean;
}

declare interface EmojiModSelection {
  large: boolean;
  mirror: boolean;
  pat: boolean;
}
