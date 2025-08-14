# Development Server Setup & Migration

This document provides information about setting up development servers for both Vite+React and Next.js projects, along with detailed migration guidance.

## Next.js Development Server Setup

### System Requirements & Installation

Based on the [official Next.js documentation](https://nextjs.org/docs/app/getting-started/installation#run-the-development-server):

**System Requirements:**
- **Node.js 18.18** or later
- **macOS, Windows (including WSL), or Linux**

### Running the Next.js Development Server

```bash
# Navigate to the Next.js project
cd nextjs-app

# Install dependencies (if not already done)
npm install

# Start the development server
npm run dev
```

### Development Server Features

1. **Access your application**: Visit `http://localhost:3000`
2. **Live editing**: Edit `app/page.tsx` and save to see updates instantly
3. **Fast Refresh**: Automatic updates without losing component state
4. **Error overlay**: Helpful error messages displayed in the browser
5. **TypeScript support**: Built-in TypeScript compilation and type checking

### Next.js Package.json Scripts

```json
{
  "scripts": {
    "dev": "next dev",        // Starts the development server
    "build": "next build",    // Builds the application for production  
    "start": "next start",    // Starts the production server
    "lint": "next lint"       // Runs ESLint with Next.js rules
  }
}
```

### Development Server Configuration

The Next.js development server provides:

- **Hot Module Replacement (HMR)**: Instant updates without page refresh
- **Automatic compilation**: TypeScript, JSX, and CSS processing
- **Error reporting**: Clear error messages in development
- **Route-based code splitting**: Automatic optimization
- **API route handling**: Integrated backend functionality

### VS Code Integration for Next.js

Enable the Next.js TypeScript plugin in VS Code:

1. Open Command Palette (`Ctrl/⌘ + Shift + P`)
2. Search for "TypeScript: Select TypeScript Version"
3. Select "Use Workspace Version"

This enables advanced type-checking and auto-completion for Next.js projects.

## Migration from Vite to Next.js

### Why Migrate from Vite to Next.js?

Based on the [official Next.js migration guide](https://nextjs.org/docs/app/guides/migrating/from-vite), here are the  reasons to migration.

### ⚠️ Client-Side Application Limitations

If you built your application with the **default Vite plugin for React**, your application is a **purely client-side application** (SPA). This architecture has several performance limitations:

### 1. Slow Initial Page Loading
- **Problem**: Browser must download and execute entire React bundle before rendering
- **Impact**: Users see blank screen during initial load  
- **Solution**: Next.js provides Server-Side Rendering (SSR) for instant content delivery

### 2. Network Waterfalls
- **Problem**: Sequential client-server requests create performance bottlenecks
- **Example**: Parent component fetches data → child waits → child fetches data
- **Solution**: Next.js allows server-side data fetching, eliminating waterfalls

```javascript
// ❌ Vite/React - Network Waterfall Pattern
function Parent() {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    // First request
    fetch('/api/parent').then(res => {
      setData(res.data);
      // Child can't start fetching until this completes
    });
  }, []);
  
  return data ? <Child parentData={data} /> : <Loading />;
}

// ✅ Next.js - Server-Side Parallel Fetching
async function Page() {
  // Both requests can happen in parallel on the server
  const [parentData, childData] = await Promise.all([
    fetch('/api/parent'),
    fetch('/api/child')
  ]);
  
  return <Parent data={parentData} childData={childData} />;
}
```

### 3. No Automatic Code Splitting
- **Problem**: Manual code splitting often introduces more performance issues
- **Solution**: Next.js provides automatic code splitting through its router

### 4. SEO Limitations
- **Problem**: Client-side rendering provides poor SEO performance
- **Solution**: Next.js supports SSR, SSG, and ISR for excellent SEO

## Key Entry Point Differences

### Vite Entry Point (`main.tsx`)
```typescript
// Vite entry point - main.tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

### Next.js Entry Point (`page.tsx`)
```typescript
// Next.js entry point - app/page.tsx
export default function Page() {
  return (
    <div>
      <h1>Hello, Next.js!</h1>
      {/* Your app content here */}
    </div>
  );
}
```

**Difference**: On Next.js you declare an entrypoint for your application by creating a `page.tsx` file. The closest equivalent of this file on Vite is your `main.tsx` file.

## Migration Steps

The [official migration guide](https://nextjs.org/docs/app/guides/migrating/from-vite) provides 9 detailed steps:

### Step 1: Install Next.js Dependency
```bash
npm install next@latest
```

### Step 2: Create Next.js Configuration
```javascript
// next.config.mjs
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export', // Outputs a Single-Page Application (SPA)
  distDir: './dist', // Changes build output directory
}

export default nextConfig
```

### Step 3: Update TypeScript Configuration
Key changes for `tsconfig.json`:
- Remove project reference to `tsconfig.node.json`
- Add `./dist/types/**/*.ts` and `./next-env.d.ts` to include array
- Add `{ "name": "next" }` to plugins array
- Set `jsx` to `"preserve"`
- Set `esModuleInterop` to `true`

### Step 4: Create Root Layout
Convert `index.html` to Next.js root layout:

```typescript
// app/layout.tsx
export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <div id="root">{children}</div>
      </body>
    </html>
  )
}
```

### Step 5: Create Entry Point Page
Replace `main.tsx` with `app/[[...slug]]/page.tsx`:

```typescript
// app/[[...slug]]/page.tsx
import '../../index.css'
import { ClientOnly } from './client'

export function generateStaticParams() {
  return [{ slug: [''] }]
}

export default function Page() {
  return <ClientOnly />
}
```

### Step 6: Environment Variables Migration
- Change `VITE_` prefix to `NEXT_PUBLIC_`
- Replace `import.meta.env.MODE` with `process.env.NODE_ENV`
- Replace `import.meta.env.PROD` with `process.env.NODE_ENV === 'production'`

### Step 7: Update package.json Scripts
```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  }
}
```

### Step 8: Clean Up Vite Files
Remove Vite-specific files:
- `main.tsx`
- `index.html`
- `vite-env.d.ts`
- `vite.config.ts`
- `tsconfig.node.json`

## Post-Migration Next Steps

After successful migration, incrementally adopt Next.js features:

1. **Migrate from React Router to Next.js App Router**
2. **Optimize images with `<Image>` component**
3. **Optimize fonts with `next/font`**
4. **Implement Server-Side Rendering (SSR)**
5. **Add API routes for backend functionality**
6. **Update ESLint configuration for Next.js**

## Architecture Comparison Summary

| Aspect | Vite (`main.tsx`) | Next.js (`page.tsx`) |
|--------|-------------------|----------------------|
| **Entry Point** | Client-side mount to DOM | Server-rendered page component |
| **Rendering** | Pure client-side | Server-side + client-side hydration |
| **Data Fetching** | useEffect + fetch | Server components + async/await |
| **Routing** | React Router (manual) | File-system based (automatic) |
| **Performance** | Network waterfalls | Optimized server rendering |
| **SEO** | Limited (CSR only) | Excellent (SSR/SSG) |

## Development Server Comparison

| Feature | Vite Development Server | Next.js Development Server |
|---------|------------------------|----------------------------|
| **Startup Time** | ⚡ Instant (~200ms) | 🔄 Fast (~2-3s) |
| **Hot Reload** | Vite HMR | Next.js Fast Refresh |
| **Debugging** | Chrome DevTools | Integrated SSR debugging |
| **Port** | 5173 (default) | 3000 (default) |
| **API Integration** | Proxy to separate server | Built-in API routes |
| **TypeScript** | External compilation | Integrated compilation |

## Summary

The migration from Vite to Next.js represents a fundamental shift from client-side rendering to a full-stack, server-side rendered architecture. While Vite excels at fast development and simple SPAs, Next.js provides better performance, SEO, and integrated full-stack capabilities for production applications.

Choose Vite when you need maximum development speed and are building SPAs or working with separate backend teams. Choose Next.js when SEO, performance, and integrated full-stack development are priorities.
