import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";
import crossOriginIsolation from 'vite-plugin-cross-origin-isolation';

// https://vitejs.dev/config/
export default defineConfig({
  open: true,
  port: 5173,
  plugins: [react(), crossOriginIsolation()],
});
