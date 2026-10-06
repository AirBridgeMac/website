import { defineConfig } from "vite";
import { fileURLToPath } from "node:url";

export default defineConfig({
  build: {
    rolldownOptions: {
      input: {
        home: fileURLToPath(new URL("./index.html", import.meta.url)),
        guide: fileURLToPath(new URL("./guide/index.html", import.meta.url)),
        privacy: fileURLToPath(
          new URL("./privacy/index.html", import.meta.url),
        ),
      },
    },
  },
});
