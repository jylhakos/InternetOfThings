# Debugging Express.js & Node.js

## 1. Start Debugging Session
```bash
# Method 1: VS Code (Recommended)
# Open VS Code → Run and Debug (Ctrl+Shift+D) → Select "Launch Express App" → F5

# Method 2: Chrome DevTools
npm run debug
# Then open chrome://inspect

# Method 3: With Environment Variables
DEBUG=express:*,app:* npm start
```

### 2. Set Breakpoints
- Click in the gutter next to line numbers in VS Code
- Strategic locations: route handlers, middleware, error handlers
- Use conditional breakpoints: right-click → "Edit Breakpoint"

### 3. Test Your Setup
```bash
# Run the test suite (already working!)
npm test

# Test API endpoints
curl http://localhost:3000
curl http://localhost:3000/users
curl http://localhost:3000/error  # Test error handling
curl http://localhost:3000/memory # Check performance
```

## 🛠 Available Tools & Commands

### Debug Commands
| Command | Purpose |
|---------|---------|
| `npm run dev` | Start with nodemon (auto-restart) |
| `npm run debug` | Start with Node.js inspector |
| `npm test` | Run comprehensive test suite |
| `./debug.sh` | Start with full debugging environment |
| `./system-check.sh` | Check system requirements |

### VS Code Debug Configurations
- **Launch Express App** - Standard debugging
- **Launch with Nodemon** - Auto-restart debugging
- **Attach to Process** - Attach to running process
- **Debug TypeScript App** - TypeScript support
- **Attach to Docker** - Container debugging

## Debugging Features

### 1. Request Tracing
Every request shows:
```
Request received: {
  method: 'GET',
  url: '/users/123',
  params: { id: '123' },
  query: {},
  headers: { ... }
}
Response sent: 200 - 15ms
```

### 2. Performance Monitoring
Automatic detection of slow requests:
```
⚠️ Slow request detected: GET /users took 106.72ms
```

### 3. Memory Tracking
Real-time memory usage at `/memory` endpoint:
```json
{
  "memory": {
    "rss": "45.23 MB",
    "heapTotal": "15.67 MB",
    "heapUsed": "12.34 MB"
  },
  "uptime": "127 seconds"
}
```

### 4. Error Handling
Detailed error information with stack traces:
```json
{
  "status": "error",
  "message": "This is a test error",
  "stack": "Error: This is a test error\n    at /path/to/file:154:19..."
}
```

### Docker Development
```bash
# Start containerized debugging
docker-compose -f docker-compose.dev.yml up --build -d
# Debug port 9229 is exposed for VS Code attachment
```

### References
- [Express.js Documentation](https://expressjs.com/)
- [VS Code TypeScript Debugging](https://code.visualstudio.com/docs/typescript/typescript-debugging)
- [Mozilla Express/Node.js Guide](https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Server-side/Express_Nodejs/Introduction)
- [Prisma Docker Guide](https://www.prisma.io/docs/guides/docker)

---
