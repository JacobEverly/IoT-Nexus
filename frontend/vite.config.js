import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import Restart from 'vite-plugin-restart';

export default defineConfig({
  plugins: [react(),
  Restart({
    restart: ['**/*']  // specify paths that should trigger a full restart
  })],
  resolve: {
    alias: [{ find: "@", replacement: "/src" }],
  },
});
