# Debug

## Quick Start

### Development Mode
```bash
# Start with nodemon (auto-restart on changes)
npm run dev

# Start with debugging enabled
npm run debug

# Start with breakpoint on first line
npm run debug-brk
```

### Debug with Environment Variables
```bash
# Enable Express internal debugging
DEBUG=express:* npm start

# Enable application-specific debugging
DEBUG=app:* npm start

# Enable all debugging
DEBUG=* npm start

# Custom debug namespace
DEBUG=app:server,app:routes,app:database npm start
```

### VS Code Debugging
1. Open project in VS Code
2. Go to Run and Debug (Ctrl+Shift+D)
3. Choose from these configurations:
   - **Launch Express App** - Start with debugging
   - **Launch with Nodemon** - Auto-restart debugging
   - **Attach to Process** - Attach to running process
   - **Debug TypeScript App** - TypeScript debugging
   - **Attach to Docker** - Docker container debugging

### Chrome DevTools Debugging
```bash
# Start with inspector
node --inspect app.js

# With custom port
node --inspect=5858 app.js

# Break on first line
node --inspect-brk app.js
```

Then:
1. Open Chrome
2. Go to `chrome://inspect`
3. Click "Open dedicated DevTools for Node"

### Testing Commands
```bash
# Run all tests
npm test

# Run tests with watch mode
npm run test:watch

# Run with coverage
npm run test:coverage

# Run specific test file
npm test test/app.test.js
```

### Docker Debugging
```bash
# Build and start containers
docker-compose -f docker-compose.dev.yml up --build -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f app

# Stop containers
docker-compose -f docker-compose.dev.yml down
```

### System Diagnostics
```bash
# Check system requirements
./system-check.sh

# Check port usage
lsof -i :3000
lsof -i :9229

# Monitor memory usage
htop

# Check application logs
tail -f /var/log/application.log
```

### API Testing
```bash
# Test basic endpoints
curl http://localhost:3000
curl http://localhost:3000/users
curl http://localhost:3000/users/123

# Test POST endpoint
curl -X POST http://localhost:3000/users \
  -H "Content-Type: application/json" \
  -d '{"name":"John Doe","email":"john@example.com"}'

# Test error handling
curl http://localhost:3000/error

# Check memory usage
curl http://localhost:3000/memory
```

### TypeScript Debugging
```bash
# Compile TypeScript
npx tsc

# Run compiled JavaScript
node dist/app.js

# Debug TypeScript directly
npx ts-node src/app.ts

# Debug with path mapping
npx ts-node -r tsconfig-paths/register src/app.ts
```

## Breakpoint Strategies

### Strategic Breakpoint Placement
1. **Route handlers** - Beginning of each route
2. **Middleware functions** - Before and after processing
3. **Error handlers** - Catch and global error handlers
4. **Database operations** - Before and after DB calls
5. **Validation logic** - Input validation points
6. **Performance bottlenecks** - Slow operations

### Conditional Breakpoints
- Right-click breakpoint → "Edit Breakpoint"
- Add condition: `userId === '123'`
- Only breaks when condition is true

### Logpoints
- Right-click in gutter → "Add Logpoint"
- Add message: `User ID: {userId}, Name: {user.name}`
- Logs without stopping execution

## Environment Variables for Debugging

### .env file
```env
NODE_ENV=development
DEBUG=express:*,app:*
PORT=3000
LOG_LEVEL=debug
```

### Production Safety
```javascript
if (process.env.NODE_ENV === 'development') {
    // Development-only debugging code
    app.use(require('morgan')('dev'));
}
```

## Common Debugging Scenarios

### 1. API Request/Response Issues
- Set breakpoints in route handlers
- Inspect `req.body`, `req.params`, `req.query`
- Check response before `res.json()`

### 2. Middleware Problems
- Debug middleware execution order
- Check `next()` calls
- Verify middleware registration

### 3. Database Connection Issues
- Check connection strings
- Debug query execution
- Monitor connection pooling

### 4. Performance Problems
- Use performance middleware
- Monitor memory usage
- Profile CPU usage

### 5. Error Handling
- Test different error conditions
- Verify error propagation
- Check error response format

## Troubleshooting Tips

### Cannot Connect to Debugger
1. Check if port 9229 is free: `lsof -i :9229`
2. Try different port: `node --inspect=5858 app.js`
3. Check firewall settings
4. Verify VS Code configuration

### Breakpoints Not Working
1. Ensure source maps are enabled
2. Check file paths in launch.json
3. Rebuild TypeScript if applicable
4. Verify sourcemap generation

### Slow Performance
1. Check for infinite loops
2. Monitor memory leaks
3. Profile async operations
4. Optimize database queries

### Tests Failing
1. Check test database setup
2. Verify mock implementations
3. Check async test handling
4. Review test isolation

## Advanced Debugging Techniques

### Memory Leak Detection
```javascript
// Monitor memory usage
setInterval(() => {
    const usage = process.memoryUsage();
    console.log('Memory:', Math.round(usage.heapUsed / 1024 / 1024), 'MB');
}, 30000);
```

### Performance Profiling
```javascript
// Measure execution time
const start = process.hrtime.bigint();
// ... operation
const end = process.hrtime.bigint();
console.log('Duration:', Number(end - start) / 1000000, 'ms');
```

### Request Tracing
```javascript
// Add unique request ID
app.use((req, res, next) => {
    req.id = Math.random().toString(36).substr(2, 9);
    next();
});
```
