# Data Flow - Vite React + ASP.NET Core

## System Overview

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                           DEVELOPMENT ENVIRONMENT                             │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌─────────────────────┐    HTTP/HTTPS     ┌──────────────────────────────┐   │
│  │                     │   Proxy Requests  │                              │   │
│  │   Vite Dev Server   │◄─────────────────►│      ASP.NET Core API        │   │
│  │                     │                   │                              │   │
│  │   React Frontend    │                   │   Controllers + Services     │   │
│  │   (localhost:5173)  │                   │   (localhost:7042)           │   │
│  │                     │                   │                              │   │
│  └─────────────────────┘                   └──────────────────────────────┘   │
│           │                                               │                   │
│           │                                               │                   │
│           │ WebSocket (HMR)                               │ Entity Framework  │
│           │                                               │                   │
│           ▼                                               ▼                   │
│  ┌─────────────────────┐                    ┌──────────────────────────────┐  │
│  │                     │                    │                              │  │
│  │   Hot Module        │                    │     SQLite Database          │  │
│  │   Replacement       │                    │     (contacts.db)            │  │
│  │   (HMR Server)      │                    │                              │  │
│  │   (localhost:5174)  │                    │   ┌──────────────────────┐   │  │
│  │                     │                    │   │   Contacts Table     │   │  │
│  └─────────────────────┘                    │   │   - Id (PK)          │   │  │
│                                             │   │   - Name             │   │  │
│                                             │   │   - PhoneNumber      │   │  │
│                                             │   │   - Email            │   │  │
│                                             │   │   - Company          │   │  │
│                                             │   │   - Category         │   │  │
│                                             │   │   - CreatedAt        │   │  │
│                                             │   │   - UpdatedAt        │   │  │
│                                             │   │   - IsActive         │   │  │
│                                             │   └──────────────────────┘   │  │
│                                             └──────────────────────────────┘  │
│                                                             │                 │
│                                                             │                 │
│                                                             ▼                 │
│                                             ┌──────────────────────────────┐  │
│                                             │                              │  │
│                                             │   Memory Cache Service       │  │
│                                             │   - Contact Cache            │  │
│                                             │   - Search Results Cache     │  │
│                                             │   - Statistics Cache         │  │
│                                             │                              │  │
│                                             └──────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           PRODUCTION ENVIRONMENT (DOCKER)                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────┐                   ┌──────────────────────────────┐ │
│  │                     │    HTTP/HTTPS     │                              │ │
│  │   Nginx Reverse     │◄─────────────────►│   Full-Stack Container       │ │
│  │   Proxy             │    (Port 80/443)  │                              │ │
│  │   (localhost:80)    │                   │   ┌─────────────────────────┐│ │
│  │                     │                   │   │   React SPA             ││ │
│  └─────────────────────┘                   │   │   (Static Files)        ││ │
│           │                                │   │   /wwwroot/*            ││ │
│           │                                │   └─────────────────────────┘│ │
│           │                                │               │              │ │
│           │                                │               │ API Calls    │ │
│           └────────────────────────────────┼───────────────┘              │ │
│                    Load Balancing           │                             │ │
│                                             │  ┌─────────────────────────┐│ │
│                                             │  │   ASP.NET Core API      ││ │
│                                             │  │   (Port 8080)           ││ │
│                                             │  │                         ││ │
│                                             │  │   • Controllers         ││ │
│                                             │  │   • Services            ││ │
│                                             │  │   • Caching             ││ │
│                                             │  │   • Validation          ││ │
│                                             │  └─────────────────────────┘│ │
│                                             └─────────────────────────────┘ │
│                                                             │               │
│                                                             │ TCP:5432      │
│                                                             ▼               │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                        DATABASE LAYER                                   ││
│  │                                                                         ││
│  │  ┌──────────────────┐           ┌──────────────────┐                    ││
│  │  │                  │           │                  │                    ││
│  │  │   PostgreSQL     │           │   Redis Cache    │                    ││
│  │  │   Database       │           │   (Optional)     │                    ││
│  │  │   (Port 5432)    │           │   (Port 6379)    │                    ││
│  │  │                  │           │                  │                    ││
│  │  │  • Persistent    │           │  • Session Cache │                    ││
│  │  │    Storage       │           │  • Query Cache   │                    ││
│  │  │  • ACID          │           │  • Rate Limiting │                    ││
│  │  │    Transactions  │           │                  │                    ││
│  │  │  • Data          │           │                  │                    ││
│  │  │    Integrity     │           │                  │                    ││
│  │  │                  │           │                  │                    ││
│  │  └──────────────────┘           └──────────────────┘                    ││
│  └─────────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────┘
```

## Detailed Data Flow Sequence

### 1. **Development Mode Data Flow**

```
User Browser → Vite Dev Server (5173) → ASP.NET API (7042) → SQLite DB
     ↑                ↑                         ↑                  ↑
     │                │ Proxy Configuration    │ Entity Framework │
     │                │ (/api/* → 7042)        │                  │
     │                │                        │                  │
     │ Hot Module     │                        │ Memory Cache     │
     │ Replacement    │                        │ Layer            │
     │ (Live Reload)  │                        │                  │
     │                │                        │                  │
     └────WebSocket────┘                        └──────────────────┘
         (5174)
```

### 2. **Production Mode Data Flow**

```
Internet → Nginx (80/443) → ASP.NET Container (8080) → PostgreSQL (5432)
                   ↑                    ↑                      ↑
                   │                    │                      │
                   │ SSL Termination    │ Connection Pooling   │ ACID Transactions
                   │ Load Balancing     │                      │ Data Persistence
                   │                    │                      │
                   │                    ▼                      │
                   │           Memory/Redis Cache              │
                   │           • Query Caching                 │
                   │           • Session Storage               │
                   │                                           │
                   └───────────────────────────────────────────┘
```

## API Request Flow

### CRUD Operations
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          API REQUEST LIFECYCLE                              │
└─────────────────────────────────────────────────────────────────────────────┘

1. CLIENT REQUEST
   React Component
   ├── fetch('/api/contacts')
   └── Headers: Content-Type, Authorization

2. VITE PROXY (Development Only)
   vite.config.ts
   ├── Proxy Rule: /api/* → https://localhost:7042
   └── CORS Handling

3. ASP.NET CORE MIDDLEWARE PIPELINE
   Program.cs
   ├── CORS Middleware
   ├── Security Headers
   ├── Authentication (if enabled)
   └── Routing Middleware

4. CONTROLLER ACTION
   ContactsController.cs
   ├── Model Validation
   ├── Authorization Checks
   └── Business Logic

5. CACHE LAYER CHECK
   CacheService.cs
   ├── Check Memory Cache
   ├── Return if Cache Hit
   └── Continue if Cache Miss

6. DATABASE TRANSACTION
   ApplicationDbContext.cs
   ├── Begin Transaction
   ├── Execute Query/Command
   ├── Commit/Rollback
   └── Connection Pooling

7. RESPONSE PROCESSING
   ├── Update Cache (if needed)
   ├── Format JSON Response
   ├── Add Security Headers
   └── Return to Client

8. CLIENT RESPONSE HANDLING
   React Component
   ├── Parse JSON
   ├── Update State
   ├── Re-render UI
   └── Error Handling
```
