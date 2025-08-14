import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

// https://vitejs.dev/config/
export default defineConfig(({ mode, command }) => {
  const env = loadEnv(mode, process.cwd(), '');
  
  // Determine backend target URL
  const getBackendTarget = () => {
    if (env.ASPNETCORE_HTTPS_PORT) {
      return `https://localhost:${env.ASPNETCORE_HTTPS_PORT}`;
    }
    if (env.ASPNETCORE_URLS) {
      return env.ASPNETCORE_URLS.split(';')[0];
    }
    return 'https://localhost:7042'; // Default ASP.NET Core HTTPS port
  };

  const target = getBackendTarget();
  
  console.log(`🎯 Vite proxy target: ${target}`);
  console.log(`🛠️ Build mode: ${mode}`);
  console.log(`📦 Command: ${command}`);

  return {
    plugins: [react()],
    
    // Development server configuration
    server: {
      port: 5173,
      host: 'localhost',
      open: false, // Don't auto-open browser
      
      // Proxy configuration for API calls
      proxy: {
        '/api': {
          target: target,
          changeOrigin: true,
          secure: false, // Allow self-signed certificates in development
          configure: (proxy, options) => {
            proxy.on('error', (err, req, res) => {
              console.log('🚨 Proxy error:', err);
            });
            proxy.on('proxyReq', (proxyReq, req, res) => {
              console.log('🔄 Proxying request:', req.method, req.url, '->', target + req.url);
            });
            proxy.on('proxyRes', (proxyRes, req, res) => {
              console.log('✅ Proxy response:', proxyRes.statusCode, req.url);
            });
          },
        },
        '/swagger': {
          target: target,
          changeOrigin: true,
          secure: false,
        },
        '/health': {
          target: target,
          changeOrigin: true,
          secure: false,
        }
      },
      
      // Hot Module Replacement configuration
      hmr: {
        overlay: true, // Show error overlay
        port: 5174,    // Custom HMR port
      },
    },

    // Preview server (for testing production build)
    preview: {
      port: 4173,
      host: 'localhost',
    },

    // Path resolution
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src'),
        '@components': path.resolve(__dirname, 'src/components'),
        '@utils': path.resolve(__dirname, 'src/utils'),
        '@services': path.resolve(__dirname, 'src/services'),
        '@types': path.resolve(__dirname, 'src/types'),
      },
    },

    // CSS configuration
    css: {
      devSourcemap: true,
      modules: {
        localsConvention: 'camelCaseOnly',
      },
    },

    // Build configuration
    build: {
      outDir: 'dist',
      sourcemap: true,
      minify: 'terser',
      target: 'es2020',
      
      // Rollup options for optimization
      rollupOptions: {
        output: {
          manualChunks: {
            // Separate vendor chunks for better caching
            vendor: ['react', 'react-dom'],
            router: ['react-router-dom'],
          },
        },
      },
      
      // Chunk size warning limit
      chunkSizeWarningLimit: 1000,
      
      // Terser options for minification
      terserOptions: {
        compress: {
          drop_console: mode === 'production', // Remove console logs in production
          drop_debugger: true,
        },
      },
    },

    // Dependency optimization
    optimizeDeps: {
      include: [
        'react',
        'react-dom',
        'react-router-dom'
      ],
    },

    // Environment variables
    define: {
      __APP_VERSION__: JSON.stringify(process.env.npm_package_version || '1.0.0'),
      __BUILD_TIME__: JSON.stringify(new Date().toISOString()),
    },

    // Base public path
    base: mode === 'production' ? './' : '/',
    
    // Asset handling
    assetsInclude: ['**/*.woff', '**/*.woff2'],
  };
});
