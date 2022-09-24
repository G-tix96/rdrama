declare var process: {
  env: Record<string, any>;
};

declare interface ChatSpeakResponse {
  username: string;
  avatar: string;
  hat: string;
  namecolor: string;
  text: string;
  text_censored: string;
  text_html: string;
  time: number;
  timestamp: string;
}

declare interface EmojiModSelection {
  large: boolean;
  mirror: boolean;
  pat: boolean;
}
