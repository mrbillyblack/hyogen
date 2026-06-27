import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { VitePWA } from "vite-plugin-pwa";

// VITE_API_PROXY points the dev server at the backend. In docker compose the
// backend is reachable as http://api:8000; for bare-metal dev override it (e.g.
// http://localhost when Caddy is up, or http://localhost:8000).
const apiProxy = process.env.VITE_API_PROXY || "http://api:8000";

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: "autoUpdate",
      includeAssets: ["favicon.svg", "apple-touch-icon.png"],
      manifest: {
        name: "Hyogen — Japanese lyrics reader",
        short_name: "Hyogen",
        description:
          "Annotate Japanese song lyrics with hiragana readings and English meanings.",
        theme_color: "#4f46e5",
        background_color: "#ffffff",
        display: "standalone",
        icons: [
          { src: "pwa-192x192.png", sizes: "192x192", type: "image/png" },
          { src: "pwa-512x512.png", sizes: "512x512", type: "image/png" },
          {
            src: "pwa-512x512.png",
            sizes: "512x512",
            type: "image/png",
            purpose: "maskable",
          },
        ],
      },
    }),
  ],
  server: {
    host: true,
    port: 5173,
    proxy: {
      "/api": { target: apiProxy, changeOrigin: true },
    },
    // Reliable file watching across the Windows/WSL bind mount.
    watch: { usePolling: true },
  },
});
