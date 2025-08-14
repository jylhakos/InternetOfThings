import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  // Development server configuration
  server: {
    port: 5173,
    host: '0.0.0.0', // Allow external connections
    open: true, // Open browser on start
    cors: true, // Enable CORS
    strictPort: false, // Don't exit if port is in use, find next available
    hmr: {
      overlay: true // Show errors in overlay
    }
  },

  // Build configuration
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: true, // Generate source maps for debugging
    minify: 'esbuild', // Use esbuild for minification (faster)
    target: 'es2020', // Target modern browsers
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['vue', 'react', 'react-dom'], // Split vendor chunks
        }
      }
    }
  },

  // Preview server configuration
  preview: {
    port: 4173,
    host: '0.0.0.0',
    open: true,
    strictPort: false
  },

  // Environment variables
  envPrefix: 'VITE_',

  // Plugin configuration (add plugins as needed)
  plugins: [
    // Add your plugins here
    // For React: react()
    // For Vue: vue()
    // For TypeScript: typescript() (if needed)
  ],

  // Resolve configuration
  resolve: {
    alias: {
      '@': '/src', // Alias for src directory
      '@components': '/src/components',
      '@assets': '/src/assets',
      '@styles': '/src/styles'
    }
  },

  // CSS configuration
  css: {
    devSourcemap: true, // Enable CSS source maps in development
    preprocessorOptions: {
      scss: {
        additionalData: `@import "@/styles/variables.scss";`
      }
    }
  },

  // Dependencies optimization
  optimizeDeps: {
    include: ['lodash', 'axios'], // Pre-bundle these dependencies
    exclude: ['@vite/client', '@vite/env'] // Don't pre-bundle these
  },

  // Define global constants
  define: {
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
    __BUILD_DATE__: JSON.stringify(new Date().toISOString())
  },

  // ESBuild configuration
  esbuild: {
    target: 'es2020',
    drop: process.env.NODE_ENV === 'production' ? ['console', 'debugger'] : []
  }
})
