# ADK TypeScript Project - Quick Start Guide

This directory contains a complete ADK TypeScript project setup ready to use in VS Code on Linux.

## What's Included

- **index.ts** - Your main agent implementation with examples
- **package.json** - Project configuration and dependencies
- **tsconfig.json** - TypeScript compiler configuration
- **.gitignore** - Excludes build artifacts, dependencies, and secrets from version control

## Setup Instructions

### 1. Install Dependencies
```bash
npm install
```

This will create a `node_modules/` directory with all required packages. This directory acts like a "virtual environment" for Node.js projects - it's specific to this project and not shared globally.

### 2. Configure Environment Variables (Optional)

Create a `.env` file for API keys (already excluded from Git):
```bash
# .env
GOOGLE_API_KEY=your_api_key_here
```

### 3. Run Your Agent

**Development Mode (with ts-node):**
```bash
npm run dev
```

**Production Mode:**
```bash
# Build first
npm run build

# Then run
npm start
```

## Working in VS Code

### Opening the Project
```bash
# Navigate to this directory
cd "/home/laptop/EXERCISES/IOT/InternetOfThings/Artificial Intelligence/CODING-AND-DEVELOPMENT/Agent Development Kit"

# Open in VS Code
code .
```

### Debugging in VS Code

1. Open [index.ts](index.ts)
2. Set breakpoints by clicking left of line numbers
3. Press **F5** to start debugging
4. Use the debug toolbar to step through code

### Useful VS Code Extensions

- **TypeScript and JavaScript Language Features** (built-in)
- **ESLint** - Code quality
- **Prettier** - Code formatting
- **GitLens** - Enhanced Git integration
- **Error Lens** - Inline error messages

### VS Code Tasks

Available npm scripts (run via VS Code terminal or command palette):

- `npm run build` - Compile TypeScript to JavaScript
- `npm run dev` - Run agent in development mode
- `npm start` - Run compiled agent
- `npm run watch` - Auto-compile on file changes
- `npm run clean` - Remove build directory

## Understanding Node.js "Virtual Environment"

Unlike Python's virtual environments (`venv`), Node.js uses:

- **node_modules/** - Local dependencies per project (like Python's `site-packages`)
- **package.json** - Dependency manifest (like `requirements.txt`)
- **package-lock.json** - Exact versions lock file

Each project has its own `node_modules/`, keeping dependencies isolated. No activation/deactivation needed!

## What's in .gitignore

The `.gitignore` file excludes:

- **node_modules/** - Dependencies (can be reinstalled)
- **dist/** - Build output (generated from source)
- **.env** - Environment variables and secrets
- **Binary files** - OS-specific executables
- **IDE files** - Editor-specific configurations
- **Logs and cache** - Temporary files

This keeps your repository clean and secure.

## Next Steps

1. Customize `index.ts` with your agent logic
2. Add custom tools to enhance agent capabilities
3. Configure environment variables for API access
4. Test your agent with different prompts
5. Deploy to Cloud Run (see main README.md)

## Troubleshooting

### "Cannot find module '@google/adk'"
```bash
npm install
```

### TypeScript errors
```bash
npm install typescript @types/node --save-dev
```

### Permission denied
```bash
chmod +x node_modules/.bin/*
```

### Build errors
```bash
npm run clean
npm run build
```

## Resources

- See [README.md](README.md) for comprehensive ADK documentation
- [ADK TypeScript Quickstart](https://google.github.io/adk-docs/get-started/typescript/)
- [VS Code TypeScript Tutorial](https://code.visualstudio.com/docs/typescript/typescript-tutorial)
