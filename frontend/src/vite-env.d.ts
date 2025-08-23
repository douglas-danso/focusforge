/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  readonly VITE_APP_NAME: string
  readonly VITE_APP_VERSION: string
  readonly VITE_DEV_TOOLS: string
  readonly VITE_GOOGLE_CLIENT_ID: string
  readonly VITE_ENABLE_ANALYTICS: string
  readonly VITE_ENABLE_NOTIFICATIONS: string
  readonly VITE_ENABLE_EXPERIMENTAL_FEATURES: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
