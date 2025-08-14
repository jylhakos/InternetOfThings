#!/bin/bash

# Architecture Visualization Script
# Generates ASCII diagrams for the Vite React + ASP.NET Core architecture

echo "📊 Vite React + ASP.NET Core Architecture Overview"
echo "=================================================="

cat << 'EOF'

                    🌐 CLIENT-SERVER DATA FLOW 🌐

Development Mode:
┌─────────────────────────────────────────────────────────────────────────┐
│                            BROWSER                                      │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                     React SPA                                   │   │
│  │                  (localhost:5173)                               │   │
│  │                                                                 │   │
│  │  Components: ContactList, ContactForm, SearchBox               │   │
│  │  State: React hooks, form validation                           │   │
│  │  API calls: fetch('/api/contacts')                             │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                │                                        │
│                        HTTP Requests                                    │
│                       (/api/contacts/*)                                 │
│                                │                                        │
└────────────────────────────────┼────────────────────────────────────────┘
                                 │
                        ┌────────▼─────────┐
                        │   Vite Proxy    │
                        │   (vite.config)  │
                        │                  │
                        │  Proxy Rules:    │
                        │  /api/* →        │
                        │  :7042/api/*     │
                        └────────┬─────────┘
                                 │
                        HTTPS/HTTP Request
                                 │
┌────────────────────────────────▼────────────────────────────────────────┐
│                        ASP.NET CORE API                                 │
│                        (localhost:7042)                                 │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                   HTTP PIPELINE                                 │   │
│  │                                                                 │   │
│  │  1. CORS Middleware ──┐                                        │   │
│  │  2. Security Headers  │                                        │   │
│  │  3. Authentication    │ Program.cs                             │   │
│  │  4. Routing           │ Configuration                          │   │
│  │  5. Controllers       │                                        │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                │                                        │
│  ┌─────────────────────────────▼─────────────────────────────────┐     │
│  │                  ContactsController                           │     │
│  │                                                               │     │
│  │  • GET    /api/contacts           (List all)                 │     │
│  │  • GET    /api/contacts/{id}      (Get by ID)                │     │
│  │  • POST   /api/contacts           (Create)                   │     │
│  │  • PUT    /api/contacts/{id}      (Update)                   │     │
│  │  • DELETE /api/contacts/{id}      (Delete)                   │     │
│  │  • GET    /api/contacts/search/{term} (Search)               │     │
│  │  • POST   /api/contacts/bulk      (Bulk create)              │     │
│  │  • GET    /api/contacts/stats     (Statistics)               │     │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                │                                        │
│  ┌─────────────────────────────▼─────────────────────────────────┐     │
│  │                    CACHE LAYER                                │     │
│  │                   (CacheService)                              │     │
│  │                                                               │     │
│  │  Cache Keys:                                                  │     │
│  │  • contact_{id}      (Individual contacts)                   │     │
│  │  • contacts_all      (Full list)                             │     │
│  │  • search_{term}     (Search results)                        │     │
│  │  • contact_stats     (Statistics)                            │     │
│  │                                                               │     │
│  │  Features:                                                    │     │
│  │  • Memory Cache with TTL                                     │     │
│  │  • Pattern-based invalidation                                │     │
│  │  • JSON serialization                                        │     │
│  │  • Performance logging                                       │     │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                │                                        │
│  ┌─────────────────────────────▼─────────────────────────────────┐     │
│  │                DATABASE LAYER                                 │     │
│  │              (ApplicationDbContext)                           │     │
│  │                                                               │     │
│  │  Entity Framework Core:                                       │     │
│  │  • Database transactions                                      │     │
│  │  • Connection pooling                                         │     │
│  │  • Query optimization                                         │     │
│  │  • Migration support                                          │     │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                │                                        │
└────────────────────────────────┼────────────────────────────────────────┘
                                 │
                     ┌───────────▼────────────┐
                     │    DATABASE ENGINE     │
                     │                        │
                     │  Development: SQLite   │
                     │  Production: PostgreSQL │
                     │                        │
                     │  Table: Contacts       │
                     │  ├── Id (PK)           │
                     │  ├── Name             │
                     │  ├── PhoneNumber      │
                     │  ├── Email            │
                     │  ├── Company          │
                     │  ├── Category         │
                     │  ├── Address          │
                     │  ├── Notes            │
                     │  ├── CreatedAt        │
                     │  ├── UpdatedAt        │
                     │  └── IsActive         │
                     └────────────────────────┘

Production Mode (Docker):
┌─────────────────────────────────────────────────────────────────────────┐
│                         INTERNET TRAFFIC                                │
└─────────────────────────┬───────────────────────────────────────────────┘
                          │
                          ▼ HTTP/HTTPS (Port 80/443)
          ┌─────────────────────────────────────────┐
          │            NGINX PROXY                  │
          │                                         │
          │  • SSL Termination                     │
          │  • Load Balancing                      │
          │  • Static File Serving                 │
          │  • Gzip Compression                    │
          │  • Security Headers                    │
          └───────────────┬─────────────────────────┘
                          │
                          ▼ Proxy Pass (Port 8080)
┌─────────────────────────┴─────────────────────────────────────────────────┐
│                    DOCKER CONTAINER                                      │
│                   (vite-react-asp:8080)                                  │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                 FULL-STACK APPLICATION                         │    │
│  │                                                                 │    │
│  │  ┌─────────────────────────────────────────────────────────┐   │    │
│  │  │              REACT SPA (Static Files)                  │   │    │
│  │  │                                                         │   │    │
│  │  │  Built with Vite:                                      │   │    │
│  │  │  • Optimized bundles                                   │   │    │
│  │  │  • Tree shaking                                        │   │    │
│  │  │  • Code splitting                                      │   │    │
│  │  │  • Asset optimization                                  │   │    │
│  │  │                                                         │   │    │
│  │  │  Served from: /wwwroot/                                │   │    │
│  │  └─────────────────────────────────────────────────────────┘   │    │
│  │                          │                                     │    │
│  │                          │ Internal API calls                 │    │
│  │                          ▼                                     │    │
│  │  ┌─────────────────────────────────────────────────────────┐   │    │
│  │  │              ASP.NET CORE API                           │   │    │
│  │  │                                                         │   │    │
│  │  │  Same architecture as development:                     │   │    │
│  │  │  • Controllers                                          │   │    │
│  │  │  • Services                                             │   │    │
│  │  │  • Caching                                              │   │    │
│  │  │  • Validation                                           │   │    │
│  │  │  • Error handling                                       │   │    │
│  │  │  • Health checks                                        │   │    │
│  │  └─────────────────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└──────────────────────────┬───────────────────────────────────────────────┘
                           │
                           ▼ Database Connection (Port 5432)
          ┌─────────────────────────────────────────┐
          │         POSTGRESQL DATABASE             │
          │                                         │
          │  • ACID Transactions                   │
          │  • Connection Pooling                  │
          │  • Persistent Storage                  │
          │  • Backup & Recovery                   │
          │  • Performance Optimization            │
          └─────────────────────────────────────────┘
                           │
                           ▼ Cache Connection (Port 6379)
          ┌─────────────────────────────────────────┐
          │            REDIS CACHE                  │
          │                                         │
          │  • Distributed Caching                 │
          │  • Session Storage                     │
          │  • Rate Limiting                       │
          │  • Pub/Sub Messaging                   │
          │  • Memory-based Performance            │
          └─────────────────────────────────────────┘

🔄 REQUEST LIFECYCLE FLOW:

1. 🌐 User opens browser → http://localhost (or https://yourdomain.com)

2. 📡 Nginx receives request:
   ├── Static files (CSS, JS, images) → Served directly
   ├── API requests (/api/*) → Proxy to ASP.NET Core container
   └── SPA routes → Return index.html (client-side routing)

3. ⚛️ React SPA loads:
   ├── Hydrates UI components
   ├── Initializes application state
   └── Makes API calls to /api/contacts

4. 🔀 ASP.NET Core processes API request:
   ├── CORS & Security middleware
   ├── Route to ContactsController
   ├── Check cache layer (CacheService)
   ├── Query database if cache miss
   ├── Apply business logic
   ├── Update cache if needed
   └── Return JSON response

5. 🗄️ Database interaction:
   ├── Entity Framework translates LINQ to SQL
   ├── Connection pool manages connections
   ├── Transaction ensures data consistency
   └── Results returned to application layer

6. ⚡ Caching layer:
   ├── Checks memory cache first
   ├── Returns cached data if available
   ├── Stores new data with TTL
   └── Invalidates cache on data changes

7. 📤 Response sent back:
   ├── JSON data serialized
   ├── Security headers added
   ├── CORS headers included
   └── Client receives response

8. 🔄 React updates UI:
   ├── State management updates
   ├── Component re-rendering
   ├── User interface refreshed
   └── Ready for next interaction

EOF

echo ""
echo "🐳 Docker Architecture:"
echo "======================"

cat << 'EOF'

DEVELOPMENT ENVIRONMENT:
┌─────────────────────────────────────────────────────────────┐
│                    Host Machine                             │
│                                                             │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐   │
│  │   Browser   │────▶│ Vite Dev    │────▶│  ASP.NET    │   │
│  │ localhost:  │     │ Server      │     │  Container  │   │
│  │   5173      │     │ :5173       │     │    :8080    │   │
│  └─────────────┘     └─────────────┘     └─────────────┘   │
│        │                    │                    │         │
│        │ Hot Reload         │ Volume Mount       │ SQLite  │
│        ▼                    ▼                    ▼         │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐   │
│  │  WebSocket  │     │./Client src │     │./Server src │   │
│  │   :5174     │     │(Live Sync)  │     │(Live Sync)  │   │
│  └─────────────┘     └─────────────┘     └─────────────┘   │
└─────────────────────────────────────────────────────────────┘

PRODUCTION ENVIRONMENT:
┌─────────────────────────────────────────────────────────────┐
│                   Docker Compose Network                    │
│                      (app-network)                          │
│                                                             │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐   │
│  │   Nginx     │────▶│Full-Stack   │────▶│ PostgreSQL  │   │
│  │   Proxy     │     │ Container   │     │ Database    │   │
│  │  :80/:443   │     │   :8080     │     │   :5432     │   │
│  └─────────────┘     └─────────────┘     └─────────────┘   │
│                              │                             │
│                              │                             │
│                              ▼                             │
│                      ┌─────────────┐                       │
│                      │   Redis     │                       │
│                      │   Cache     │                       │
│                      │   :6379     │                       │
│                      └─────────────┘                       │
│                                                             │
│  Persistent Volumes:                                        │
│  ├── postgres_data                                          │
│  ├── redis_data                                             │
│  └── nginx_ssl                                              │
└─────────────────────────────────────────────────────────────┘

EOF

echo ""
echo "✅ Architecture Components Summary:"
echo "=================================="
echo "📱 Frontend: React SPA with Vite build system"
echo "🔧 Backend: ASP.NET Core Web API with Entity Framework"
echo "💾 Database: SQLite (dev) / PostgreSQL (prod)"
echo "⚡ Cache: Memory Cache (dev) / Redis (prod)"
echo "🌐 Proxy: Vite dev proxy (dev) / Nginx (prod)"
echo "🐳 Containerization: Docker with multi-stage builds"
echo "🔄 Hot Reload: Vite HMR + dotnet watch (dev only)"
echo "🔒 Security: CORS, Security headers, SSL termination"
echo "📊 Monitoring: Health checks, logging, metrics"
echo "🚀 Deployment: Docker Compose with environment overrides"
