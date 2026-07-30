import { fileURLToPath, URL } from "node:url";

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: "2025-05-15",
  devtools: { enabled: true },

  css: ["~/assets/css/main.css"],

  // Three roles: Archivo carries the industrial signage voice at display
  // sizes, Instrument Sans reads quietly at body sizes, and IBM Plex Mono
  // sets every figure with tabular numerals so columns of money line up.
  fonts: {
    families: [
      { name: "Archivo", provider: "google", weights: [600, 700, 800] },
      { name: "Instrument Sans", provider: "google", weights: [400, 500, 600] },
      { name: "IBM Plex Mono", provider: "google", weights: [400, 500] },
    ],
  },

  modules: [
    "@nuxt/eslint",
    "@nuxt/fonts",
    "@nuxt/icon",
    "@nuxt/image",
    "@nuxt/scripts",
    "@nuxt/test-utils",
    "@nuxt/ui",
    "nuxt-security",
    "@pinia/nuxt",
    "pinia-plugin-persistedstate/nuxt",
  ],
  runtimeConfig: {
    public: {
      baseUrl: "http://localhost:8000",
    },
  },
  security: {
    corsHandler: {
      // NUXT_PUBLIC_BASE_URL already overrides runtimeConfig.public.baseUrl at
      // runtime; this list is not auto-overridable, so it reads env directly.
      origin: (
        process.env.NUXT_CORS_ORIGINS ??
        "http://localhost:3000,http://localhost:8000"
      ).split(","),
      methods: ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
      allowHeaders: ["Content-Type", "Authorization"],
      exposeHeaders: ["Content-Length", "X-Total-Count"],
      credentials: true,
      maxAge: "600",
      preflight: {
        statusCode: 204,
      },
    },
  },
  alias: {
    "@": fileURLToPath(new URL(".", import.meta.url)),
  },
  imports: {
    dirs: ["store", "composables"],
  },
});
