# Backend Dockerfile
FROM node:18-alpine AS backend-builder

WORKDIR /app/backend

# Copy package files
COPY backend/package*.json ./

# Install dependencies
RUN npm ci --only=production && npm cache clean --force

# Copy source code
COPY backend/src ./src

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S backend -u 1001

USER backend

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node healthcheck.js || exit 1

# Start the application
CMD ["node", "src/server.js"]
