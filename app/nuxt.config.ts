// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: "2025-05-15",
  devtools: { enabled: true },

  css: ["~/assets/css/main.css"],

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
  ],
  runtimeConfig: {
    public: {
      baseUrl: "http://localhost:8000",
    },
  },

  security: {
    corsHandler: {
      origin: ["http://localhost:3000", "http://localhost:8000"],
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
});