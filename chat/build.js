require('dotenv').config()
const path = require("path");
const { build } = require("esbuild");

const options = {
  entryPoints: ["./src/index.tsx"],
  outfile: path.resolve(__dirname, "../files/assets/js/chat_done.js"),
  bundle: true,
  minify: process.env.NODE_ENV === "production",
  define: {
    "process.env.NODE_ENV": `"${process.env.NODE_ENV}"`,
    "process.env.DEBUG": process.env.DEBUG,
    "process.env.FEATURES_ACTIVITY": process.env.FEATURES_ACTIVITY,
    "process.env.EMOJI_INPUT_TOKEN": `"${process.env.EMOJI_INPUT_TOKEN}"`,
    "process.env.QUICK_EMOJIS_MAX_COUNT": process.env.QUICK_EMOJIS_MAX_COUNT,
    "process.env.APPROXIMATE_CHARACTER_WIDTH": process.env.APPROXIMATE_CHARACTER_WIDTH,
  },
};

build(options).catch(() => process.exit(1));
