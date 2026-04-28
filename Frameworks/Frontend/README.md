# Frontend Frameworks

A collection of frontend frameworks covering web and mobile application development. Each sub-folder demonstrates a technology stack with backend integration, database connectivity, and deployment tooling.

## Repository Structure

```
📁 Frontend/
├── 📁 Flutter/          Single Page Application with AWS integration
├── 📁 NextJS/           Server-side rendered web application with Prisma ORM
├── 📁 React/            Component-based UI with Redux and Axios
├── 📁 ReactNative/      Cross-platform mobile application with Expo
├── 📁 Svelte/           SvelteKit SPA with Android deployment via Capacitor
├── 📁 Vite/             Vite build tooling setup and migration to Next.js
└── 📁 Vue/              Vue.js application with Vite and VS Code debugging
```

---

## Flutter

**Topic**: Single Page Application (SPA) targeting Android, Chrome tablet (PWA), and Apple iPad iOS, backed by Node.js and deployed to Amazon AWS.

### Folder Structure

```
📁 Flutter/
├── 📄 docker-compose.yml        Multi-container orchestration
├── 📄 Dockerfile                Container build configuration
├── 📄 nginx.conf                Reverse proxy and load balancer
├── 📄 pubspec.yaml              Flutter dependencies and AWS integration
├── 📁 backend/
│   ├── 📄 Dockerfile
│   ├── 📄 package.json
│   └── 📁 src/
│       ├── 📄 server.js         Express server with CORS and middleware
│       ├── 📁 config/           MongoDB connection configuration
│       ├── 📁 models/           Mongoose user schema and validation
│       ├── 📁 middleware/       JWT authentication middleware
│       └── 📁 routes/           Authentication and user management routes
├── 📁 lib/
│   ├── 📄 main.dart             App entry point with Riverpod and GoRouter
│   ├── 📁 models/               User data model and API response wrapper
│   ├── 📁 services/             AWS Cognito auth, HTTP client, secure storage
│   └── 📁 screens/             Login, home dashboard, and profile screens
├── 📁 web/
│   ├── 📄 index.html            Flutter web entry point
│   └── 📄 manifest.json         PWA manifest configuration
└── 📁 scripts/
    ├── 📄 setup-dev.sh          Development environment automation
    ├── 📄 deploy.sh             AWS deployment automation
    ├── 📄 deploy-mongodb-aws.sh MongoDB deployment to AWS
    ├── 📄 mongodb-dev.sh        Local MongoDB development helper
    ├── 📄 mongodb-health.sh     MongoDB health check
    └── 📄 test-api.sh           API testing and validation
```

### Summary

The Flutter project implements a multi-platform Single Page Application that runs on Android as a native app, on Chrome tablet as a Progressive Web App, and on Apple iPad iOS as both a native and hybrid web application. The Dart/Flutter frontend uses the Riverpod state management library and GoRouter for navigation, and communicates with a Node.js/Express backend secured by Amazon AWS Cognito for authentication and JWT tokens for session management. User data is persisted in MongoDB, which can be deployed to AWS using the provided shell scripts. Docker Compose orchestrates the frontend, backend, and Nginx reverse proxy for both local development and production environments. AWS deployment automation covers ECS, ECR, and related infrastructure provisioning.

**Tech Stack**: Flutter (Dart), Riverpod, GoRouter, Node.js, Express.js, MongoDB, Amazon AWS (Cognito, ECS, ECR), Docker, Nginx

---

## NextJS

**Topic**: Full-stack web application combining Next.js for server-side rendering with an Express.js backend API and PostgreSQL via Prisma ORM.

### Folder Structure

```
📁 NextJS/
├── 📄 docker-compose.yml        Multi-container orchestration
├── 📄 Dockerfile                Container build configuration
├── 📄 next.config.mjs           Next.js configuration
├── 📄 package.json              Dependencies and scripts
├── 📄 server.js                 Custom Express.js server entry point
├── 📄 tailwind.config.js        Tailwind CSS configuration
├── 📁 components/
│   ├── 📄 Header.js             Site header component
│   ├── 📄 Footer.js             Site footer component
│   ├── 📄 Layout.js             Page layout wrapper
│   ├── 📄 LoadingSpinner.js     Loading state component
│   └── 📄 ErrorMessage.js       Error display component
├── 📁 lib/
│   ├── 📄 api.js                HTTP client utilities
│   ├── 📄 db.ts                 Prisma database client
│   ├── 📁 api/                  API route handlers
│   ├── 📁 env/                  Environment variable validation
│   └── 📁 middleware/           Custom Express middleware
├── 📁 pages/
│   ├── 📄 _app.js               Global application wrapper
│   ├── 📄 index.js              Home page
│   ├── 📄 quotes.js             Quotes page
│   ├── 📄 analytics.js          Analytics page
│   ├── 📁 blog/                 Blog section pages
│   └── 📁 products/             Products section pages
├── 📁 prisma/
│   ├── 📄 schema.prisma         Database schema definition
│   └── 📄 seed.ts               Database seed script
├── 📁 styles/
│   └── 📄 globals.css           Global CSS styles
├── 📁 docker/
│   └── 📁 nginx/                Nginx configuration for Docker
└── 📁 scripts/
    ├── 📄 dev-setup.sh          Development environment setup
    ├── 📄 deploy.sh             Production deployment script
    ├── 📄 backup-db.sh          PostgreSQL database backup
    ├── 📄 restore-db.sh         PostgreSQL database restore
    └── 📄 health-check.sh       Application health monitoring
```

### Summary

The NextJS project demonstrates a production-ready web application that uses Next.js 15 with the Pages Router for server-side rendering and static site generation, paired with a custom Express.js server for advanced backend API logic. Prisma ORM connects to a PostgreSQL database and provides type-safe database access along with a seed script for initial data. Tailwind CSS handles styling across reusable components such as the layout wrapper, header, footer, loading spinner, and error message. The project supports VS Code launch configurations for server-side and client-side debugging. Docker Compose and Nginx handle containerised deployment, and the included shell scripts cover database backup and restore, automated deployment, and health monitoring.

**Tech Stack**: Next.js 15, React, Express.js, Node.js 20, PostgreSQL, Prisma ORM, Tailwind CSS, TypeScript, Webpack 5, Docker, Nginx

---

## React

**Topic**: Component-based user interface built with React, Redux, and Axios for HTTP communication with a Node.js backend.

### Folder Structure

```
📁 React/
├── 📄 package.json              Dependencies and npm scripts
├── 📁 public/
│   ├── 📄 index.html            HTML entry point
│   ├── 📄 manifest.json         Web app manifest
│   └── 📄 robots.txt            Search engine directives
└── 📁 src/
    ├── 📄 App.js                Root application component
    ├── 📄 index.js              React DOM entry point
    └── 📁 components/
        └── 📄 Note.js           Note component with Redux and Axios
```

### Summary

The React project provides a foundational example of building a user interface with React, using JSX for declarative component rendering and Redux for predictable application state management. Axios handles HTTP requests to a backend API, demonstrating the standard React data-fetching pattern. The application is bootstrapped with Create React App, runs in development mode via `npm start`, and illustrates how React Core and ReactDOM work together to render components into the browser DOM. The `Note` component in `src/components/` serves as a practical example of connecting React components to Redux state and performing asynchronous HTTP operations.

**Tech Stack**: React, Redux, JSX, Axios, Node.js, HTML, CSS

---

## ReactNative

**Topic**: Cross-platform mobile application built with React Native and Expo, targeting Android and iOS, with MongoDB as the data source.

### Folder Structure

```
📁 ReactNative/
└── 📁 albums/
    ├── 📄 App.js                Root application component
    ├── 📄 app.json              Expo application configuration
    ├── 📄 babel.config.js       Babel transpiler configuration
    ├── 📄 package.json          Dependencies and scripts
    └── 📁 assets/               Images and static resources
```

### Summary

The ReactNative project demonstrates a cross-platform mobile application using React Native and the Expo development toolchain. JSX syntax is used to define native UI components that render on both Android and iOS without platform-specific code. The `albums` sub-project uses React Native's `FlatList` component with a `renderItem` callback to display a list of data items retrieved from MongoDB. The application is built and run on an Android emulator or iOS simulator using the `expo run` command. The mongo shell commands included in the documentation illustrate how to manage the MongoDB collection that backs the application.

**Tech Stack**: React Native, Expo, JSX, JavaScript, MongoDB

---

## Svelte

**Topic**: SvelteKit Single Page Application with a Node.js/Express backend and PostgreSQL database, packaged for Android deployment using Capacitor.

### Folder Structure

```
📁 Svelte/
├── 📄 capacitor.config.ts       Capacitor Android deployment configuration
├── 📄 docker-compose.yml        Multi-container orchestration
├── 📄 Dockerfile.frontend       Frontend container build configuration
├── 📄 package.json              Frontend dependencies and scripts
├── 📄 svelte.config.js          SvelteKit configuration
├── 📄 vite.config.ts            Vite build configuration
├── 📄 tsconfig.json             TypeScript configuration
├── 📁 src/
│   ├── 📄 app.css               Global application styles
│   ├── 📄 app.html              HTML shell template
│   ├── 📁 lib/
│   │   ├── 📄 api.ts            API client for backend communication
│   │   ├── 📄 index.ts          Library exports
│   │   ├── 📄 utils.ts          Utility functions
│   │   ├── 📁 assets/           Static assets
│   │   ├── 📁 components/       Reusable Svelte components
│   │   └── 📁 stores/           Svelte writable stores for state management
│   └── 📁 routes/
│       ├── 📄 +layout.svelte    Root layout component
│       └── 📄 +page.svelte      Home page component
├── 📁 backend/
│   ├── 📄 Dockerfile            Backend container build configuration
│   ├── 📄 package.json          Backend dependencies and scripts
│   ├── 📁 src/                  Express API source code
│   └── 📁 tests/                Jest test suite for the backend API
├── 📁 nginx/
│   ├── 📄 default.conf          Default Nginx server block
│   └── 📄 nginx.conf            Main Nginx configuration
└── 📁 build/                    Compiled production output
```

### Summary

The Svelte project builds a SvelteKit SPA in TypeScript that communicates with a Node.js/Express REST API backed by PostgreSQL. Authentication is implemented with JWT tokens and bcrypt password hashing. The frontend uses Svelte writable stores for reactive state management and the SvelteKit file-based routing system. Security measures in the backend include Helmet headers, CORS policy enforcement, rate limiting, and input validation. Docker Compose coordinates the frontend, backend, and Nginx reverse proxy, while Capacitor packages the compiled SvelteKit output as an Android application. A Jest test suite validates the backend API endpoints.

**Tech Stack**: SvelteKit, TypeScript, Vite, Node.js, Express.js, PostgreSQL, JWT, bcrypt, Capacitor, Docker, Nginx, Jest

---

## Vite

**Topic**: Vite build tooling setup for JavaScript and TypeScript projects on Linux, including a Vite+React sub-project and a Next.js sub-project, with migration guidance between the two.

### Folder Structure

```
📁 Vite/
├── 📄 index.html                Vite application entry HTML
├── 📄 vite.config.ts            Root Vite configuration
├── 📄 tsconfig.json             TypeScript configuration
├── 📄 package.json              Root dependencies and scripts
├── 📄 docker-compose.yml        Multi-container orchestration
├── 📄 Dockerfile                Production container
├── 📄 Dockerfile.dev            Development container
├── 📄 nginx.conf                Nginx reverse proxy configuration
├── 📄 eslint.config.js          ESLint configuration
├── 📄 build.sh                  Production build script
├── 📄 MIGRATION.md              Migration guide from Vite to Next.js
├── 📄 COMPARISON.md             Vite vs Next.js feature comparison
├── 📁 src/
│   ├── 📄 app.ts                Application bootstrap
│   ├── 📄 main.ts               Entry point
│   └── 📁 styles/               Global stylesheets
├── 📁 vite-react-app/
│   ├── 📄 index.html
│   ├── 📄 vite.config.ts
│   ├── 📄 package.json
│   ├── 📄 tsconfig.json
│   ├── 📁 src/
│   │   ├── 📄 App.tsx           Root React component
│   │   ├── 📄 main.tsx          React DOM entry point
│   │   ├── 📁 components/       Reusable React components
│   │   ├── 📁 services/         API service layer
│   │   └── 📁 types/            TypeScript type definitions
│   └── 📁 server/               Development server utilities
└── 📁 nextjs-app/
    ├── 📄 next.config.js
    ├── 📄 package.json
    ├── 📄 tailwind.config.js
    ├── 📄 tsconfig.json
    ├── 📄 docker-compose.yml
    ├── 📄 Dockerfile
    ├── 📄 Dockerfile.dev
    ├── 📁 src/
    │   ├── 📁 app/              Next.js App Router pages and layouts
    │   ├── 📁 components/       Shared React components
    │   ├── 📁 lib/              Utility functions
    │   └── 📁 types/            TypeScript type definitions
    └── 📄 DEPLOYMENT.md         Deployment instructions for the Next.js app
```

### Summary

The Vite project serves as a tutorial and reference for setting up Vite on Linux/Debian with Node.js 18 or higher, covering project creation, TypeScript configuration, development server options, VS Code debugging, and Docker-based DevOps builds. Two complete sub-projects are included: `vite-react-app` provides a React application in TypeScript using Vite as the build tool, while `nextjs-app` provides an equivalent application using the Next.js App Router with Tailwind CSS. The `MIGRATION.md` and `COMPARISON.md` documents guide the transition from Vite+React to Next.js, comparing their routing models, rendering strategies, and deployment requirements.

**Tech Stack**: Vite 6.x, React, TypeScript, Next.js (App Router), Tailwind CSS, Node.js, Docker, Nginx, ESLint

---

## Vue

**Topic**: Vue.js application development and debugging setup using Vite as the build tool, with VS Code integration and Vue DevTools.

### Folder Structure

```
📁 Vue/
├── 📄 README.md                 Setup and debugging documentation
└── 📄 .gitignore                Git exclusion rules
```

### Summary

The Vue project documents the setup and debugging workflow for Vue.js applications on Linux using Vite as the recommended build tool. New projects are scaffolded with `npm create vue@latest`, which generates a Vite-powered project with optional TypeScript, Vue Router, Pinia state management, and ESLint configuration. Debugging is covered in two forms: browser-based debugging using the Vue.js DevTools extension and the browser Sources panel, and editor-based debugging using VS Code launch configurations attached to the Vite development server. The Vite plugin `vite-plugin-vue-devtools` provides enhanced component inspection and timeline views during development. Node.js 18.3 or higher is required.

**Tech Stack**: Vue.js, Vite, TypeScript, Node.js, Vue DevTools, ESLint

---

## The Evolving Landscape of Frontend Development

Software development for frontend applications is undergoing a fundamental shift. For decades, building a Single Page Application (SPA) meant manually writing every component, wiring up state management, configuring build tools, and maintaining test suites by hand. That model is being replaced by a new paradigm in which AI agents handle large portions of the development lifecycle autonomously, while developers focus on goals, constraints, and creative direction rather than line-by-line implementation.

AI tools such as GitHub Copilot, Cursor, and Lovable are integrating directly into existing frameworks like React, Vite, Tailwind CSS, and Next.js. Rather than replacing those frameworks, AI agents accelerate and automate the workflows built on top of them. Frontend development is shifting from manual coding toward high-level orchestration, where developers manage autonomous AI agents to build, test, and optimise interfaces.

---

## What is Agentic Coding?

Agentic coding is a development approach in which an AI agent is given a goal and autonomously plans, writes, tests, and refines code to achieve that goal, iterating through multiple steps without requiring step-by-step human instruction. Unlike simple code completion, an agentic coding system can read the existing codebase, reason about the changes required, execute commands in a terminal, observe the results, and self-correct when errors occur.

Agentic coding is not about replacing developers. It is about removing the repetitive, mechanical parts of development so that developers can spend more time on architecture, product decisions, and creative problem-solving.

---

## What is a Coding Agent?

A coding agent is an AI system that can autonomously perform software development tasks end to end. It combines a large language model with a set of tools, such as file system access, terminal execution, and web search, and operates within a feedback loop that allows it to observe outcomes and adjust its approach.

Examples of coding agents include:

- **GitHub Copilot** — An AI pair programmer embedded in VS Code and other editors that suggests code completions, generates entire functions, and answers questions about the codebase.
- **Claude Code** — Anthropic's agent for frontend and full-stack development that operates in the terminal, reads the project structure, writes and edits files, runs builds and tests, and iterates until the task is complete.
- **Cursor** — An AI-first code editor that allows developers to describe changes in natural language and have the agent apply them across multiple files simultaneously.
- **Lovable** — A web-based agent that generates complete React SPAs from natural language descriptions, screenshots, or Figma links.

---

## What are AI Agents in Software Development?

AI agents in software development are intelligent systems that can autonomously perform development tasks, make decisions, and learn from experience. AI coding agents use machine learning to understand context, generate code from natural language descriptions, and provide intelligent suggestions.

For example, Lovable is changing the way software is created. Non-technical users can create full-stack web applications using natural language, enabling anyone to bring ideas to life without coding expertise or undergoing complex development processes. Agents scan entire UI repositories to spot inconsistencies in design systems, suggest accessibility improvements, and proactively refactor component structures.

Single Page Application (SPA) development is shifting from manual coding toward high-level orchestration, where developers manage autonomous AI agents to build, test, and optimise interfaces. Instead of building components from scratch, developers define goals and constraints, then leverage agents to generate entire functional application structures covering both frontend and backend. Frontend developers can use agents like Claude Code.

AI agents can now assist across every stage of the application lifecycle, from planning and refactoring to testing, deployment, and running production systems. AI agents are transforming UI development for SPAs by shifting the focus from manual coding to intelligent orchestration, enabling faster prototyping and reducing development time from months to days. Agents can create UI components and layouts dynamically in real-time, tailoring interfaces to individual users. AI tools like Cursor and Lovable leverage well-established UI frameworks like Tailwind CSS.

AI agents generate Single Page Applications with React by utilising iterative reasoning-action loops and specialised toolsets to automate the standard software development lifecycle (SDLC). Agents use CLI tools to initialise a React project, often using Vite or Next.js, configure React Router, set up the development environment, and configure vitest.config.ts or setup.ts for testing.

### Characteristics of AI Agents

**Autonomy**: They operate without constant human intervention, executing multi-step tasks from a single high-level instruction.

**Reactivity**: They respond to changes in their environment, such as a failing test, a compiler error, or an updated requirement, and adapt their approach accordingly.

**Proactivity**: They take the initiative to achieve their objectives, anticipating what is needed next rather than waiting for explicit instruction at every step.

---

## Use Cases

### Code Generation and Completion

AI coding assistants like GitHub Copilot serve as intelligent pair programmers, suggesting code completions, generating entire functions, and even creating code from natural language descriptions. An agent can analyse the existing architecture of a project and generate new components that follow the same conventions, saving significant development time.

### Testing and Quality Assurance

AI agents excel at creating test suites, recognising test cases, and maintaining test coverage as code evolves. An agent can inspect a React component, determine what behaviours should be tested, and produce a full test file using Vitest and React Testing Library without requiring the developer to write a single test manually.

### Documentation

AI agents autonomously create, update, and manage documentation. As code changes, an agent can detect which documentation is stale, regenerate the relevant sections, and keep API references and README files aligned with the current state of the codebase.

---

## Building the UI with Lovable

Lovable generates SPAs (Single Page Applications) by using AI agents to interpret natural language prompts, transforming them into functional React codebases using Vite, TypeScript, and Tailwind CSS. Users describe the application they want, upload screenshots, or provide Figma links. Lovable acts as the coder, generating React components and handling styling using Tailwind CSS. Users can ask the AI to make changes, such as adding features or modifying styling, through conversational prompts.

**Tech Stack used by Lovable**: React, Vite, TypeScript, Tailwind CSS

Reference: [Lovable Documentation](https://docs.lovable.dev/introduction/welcome)

---

## Vibe Coding

Vibe coding refers to a method of coding where you focus entirely on the logic and creativity of what you are building, rather than the syntax, boilerplate, and mechanical details of implementation. The term captures the feeling of being in a creative flow state while building software, where the gap between an idea and a working implementation is minimal.

In practice, vibe coding means describing what you want in natural language, reviewing and guiding the output of an AI agent, and iterating rapidly on the result. The developer's role shifts from typing code to curating, directing, and refining. Attention moves toward product thinking: what should this feature do, how should it feel to the user, and what edge cases matter, rather than how to write the loop or configure the build step.

Vibe coding is enabled by the same agentic tools described in this document. Agents like Lovable, Cursor, and Claude Code reduce the cost of acting on an idea to the point where experimentation becomes the default mode of development.

---

## Workflow (ReAct Loop)

AI agents that perform coding tasks typically follow a structured Reasoning and Acting (ReAct) loop. This loop allows the agent to break down a complex task, take actions using available tools, observe the results, and iterate until the goal is achieved.

Claude Code agents use a ReAct loop to solve complex coding tasks:

**Plan**: The agent analyses the user prompt and the existing code. It identifies the components that need to be created or modified, the state management requirements, the API routes involved, and any configuration changes that are necessary.

**Act**: The agent uses available tools, including filesystem access and terminal execution, to write or modify code. It can create new files, edit existing components, install packages, and run CLI commands.

**Verify**: The agent runs local builds or unit tests using Vitest and React Testing Library, inspects the output for errors, and self-corrects. If a test fails or a build error occurs, the agent re-enters the Plan step with the new information.

This loop repeats until the task is complete and all verifications pass. The ReAct pattern is what distinguishes a coding agent from a simple autocomplete tool: the agent does not produce a single output and stop; it operates in a cycle of reasoning, action, and observation.

Reference: [The Future of AI in Software Development](https://www.microsoft.com/en-us/software-development-companies/resources/articles/future-of-ai-software-development)

---

## Prerequisites

All projects require **Node.js 18.x or higher** and **npm**. Projects using containerised deployment additionally require **Docker** and **Docker Compose**. The Flutter project requires the **Flutter SDK** and the **AWS CLI** for cloud deployment. The ReactNative project requires the **Expo CLI** and either an Android emulator or iOS simulator.

## Getting Started

Navigate into the relevant sub-folder and follow the instructions in its `README.md` file. Each project provides its own installation and run commands, typically:

```bash
npm install
npm run dev
```

For containerised projects:

```bash
docker-compose up --build
```
