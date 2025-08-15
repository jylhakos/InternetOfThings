# Development and Debugging Setup for Vue.js

This document helps to set up and debug Vue.js applications using Vite, the recommended and default build tool for new Vue projects.

## Prerequisites

- **Node.js**: Install version 18.3 or higher from [nodejs.org](https://nodejs.org/)
- **VS Code**: Recommended IDE with [Vue - Official extension](https://marketplace.visualstudio.com/items?itemName=Vue.volar)
- **Browser**: Chrome or Firefox with Vue.js DevTools extension

## Creating a New Vue Application

Create a new Vue.js project using the official scaffolding tool:

```bash
npm create vue@latest my-vue-app
cd my-vue-app
npm install
npm run dev
```

This will create a Vite-powered Vue project with optional features like TypeScript, Router, Testing, and ESLint.

## Debugging Setup Steps

### 1. Browser Developer Tools

#### Console Debugging
- Use `console.log()`, `console.error()`, and `console.warn()` statements in your code
- Access the browser console via F12 or Ctrl+Shift+I

#### Setting Breakpoints
- Open Developer Tools (F12)
- Navigate to the **Sources** tab
- Set breakpoints directly in your `.vue` component files or JavaScript/TypeScript files
- Code execution will pause at breakpoints, allowing variable inspection and step-through debugging

### 2. Vue DevTools Integration

#### Browser Extension Installation
Install the official Vue.js DevTools browser extension:
- **Chrome**: [Vue.js DevTools](https://chrome.google.com/webstore/detail/vuejs-devtools/nhdogjmejiglipccpnnnanhbledajbpd)
- **Firefox**: Available in Firefox Add-ons

#### Vite Plugin Setup
For enhanced debugging capabilities, install the Vue DevTools Vite plugin:

```bash
npm add -D vite-plugin-vue-devtools
```

Add to your `vite.config.js` or `vite.config.ts`:

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
})
```

#### Features
- **Component Inspector**: Right-click on components to inspect them
- **Time Travel Debugging**: Navigate through state changes in Vuex/Pinia
- **Performance Monitoring**: Track component render times
- **State Management**: Live-edit data properties and see immediate changes

### 3. VS Code IDE Integration

#### Launch Configuration
Create a `.vscode/launch.json` file in your project root:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "chrome",
      "request": "launch",
      "name": "Debug Vue App",
      "url": "http://localhost:5173",
      "webRoot": "${workspaceFolder}/src",
      "breakOnLoad": true,
      "sourceMapPathOverrides": {
        "webpack:///src/*": "${webRoot}/*"
      }
    }
  ]
}
```

#### Debugging Workflow
1. Set breakpoints in your VS Code editor by clicking in the gutter next to line numbers
2. Start your development server: `npm run dev`
3. Open the Debug panel (Ctrl+Shift+D)
4. Select "Debug Vue App" configuration
5. Press F5 or click the green play button

#### VS Code Extensions
- **Vue - Official** (Vue.volar): Syntax highlighting, IntelliSense, and debugging
- **Vue VSCode Snippets**: Code snippets for faster development
- **Debugger for Chrome**: Required for browser debugging integration

### 4. Advanced Debugging Techniques

#### Source Maps
Vite automatically generates source maps in development mode. For production debugging, ensure source maps are enabled in `vite.config.js`:

```typescript
export default defineConfig({
  build: {
    sourcemap: true
  }
})
```

#### Debugger Statement
Use the native `debugger` statement directly in your code:

```javascript
export default {
  data() {
    return {
      message: 'Hello Vue!'
    }
  },
  mounted() {
    debugger; // Execution will pause here when DevTools are open
    console.log('Component mounted');
  }
}
```

**Important**: Remove `debugger` statements before production deployment.

#### Network Debugging
- Monitor API requests in the Network tab of DevTools
- Use browser's built-in request/response inspection
- Set up proxy configurations in Vite for API debugging

### 5. Development Server Configuration

#### Vite Development Server
The default Vite dev server runs on `http://localhost:5173` with:
- Hot Module Replacement (HMR)
- Fast refresh for Vue components
- Automatic source map generation
- Built-in proxy support for API calls

#### Custom Configuration
Modify `vite.config.js` for custom debugging needs:

```typescript
export default defineConfig({
  server: {
    port: 3000,
    open: true, // Auto-open browser
    cors: true,
    proxy: {
      '/api': 'http://localhost:8080' // Proxy API calls
    }
  }
})
```

### 6. Testing and Debugging

#### Unit Testing with Vitest
Add Vitest for component testing:

```bash
npm add -D vitest @vue/test-utils jsdom
```

Debug tests with breakpoints in VS Code or browser.

#### E2E Testing
Consider Playwright or Cypress for end-to-end testing with debugging capabilities.

## Production Debugging

### Building for Production
```bash
npm run build
```

### Preview Production Build
```bash
npm run preview
```

### Source Maps in Production
Enable source maps for production debugging, but be aware of security implications:

```typescript
export default defineConfig({
  build: {
    sourcemap: 'hidden' // Generates source maps but doesn't reference them in bundle
  }
})
```

## Troubleshooting Common Issues

1. **DevTools not showing Vue tab**: Ensure you're running the development build, not production/minified version
2. **Breakpoints not hitting**: Verify source map generation and paths in launch configuration
3. **HMR not working**: Check for syntax errors and ensure proper component export
4. **CORS issues**: Configure proxy in Vite config for API calls

## References

- [Vue.js Official Guide](https://vuejs.org/guide/quick-start)
- [Vue DevTools Vite Plugin](https://devtools.vuejs.org/guide/vite-plugin)
- [VS Code Vue Debugging Cookbook](https://vuejs.org/guide/scaling-up/tooling#ide-support)
- [Vite Documentation](https://vitejs.dev/)
- [Vue.js DevTools GitHub](https://github.com/vuejs/devtools)

## Resources

- [Vue.js Official Documentation](https://vuejs.org/)
- [Vite Official Documentation](https://vitejs.dev/)
- [Vue Test Utils](https://test-utils.vuejs.org/)
- [Vue Router](https://router.vuejs.org/)
- [Pinia State Management](https://pinia.vuejs.org/)
