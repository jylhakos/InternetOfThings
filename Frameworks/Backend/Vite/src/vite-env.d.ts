/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_APP_TITLE: string;
  readonly VITE_API_URL: string;
  // Add more env variables as needed
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
  readonly hot?: {
    accept: (path?: string, callback?: (module: any) => void) => void;
    dispose: (callback: () => void) => void;
    decline: () => void;
    invalidate: () => void;
    on: (event: string, callback: (...args: any[]) => void) => void;
  };
}
