# Multi-stage build for React frontend
FROM node:18-alpine AS base

# Install dumb-init for proper signal handling
RUN apk add --no-cache dumb-init

# Create app directory and user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S reactuser -u 1001

WORKDIR /app

# Development stage
FROM base AS development
ENV NODE_ENV=development

# Copy package files
COPY package*.json ./
RUN npm ci

# Copy source code
COPY . .
RUN chown -R reactuser:nodejs /app

USER reactuser
EXPOSE 3000

# Use dumb-init for development
ENTRYPOINT ["dumb-init", "--"]
CMD ["npm", "start"]

# Build stage
FROM base AS build
ENV NODE_ENV=production

# Copy package files and install dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy source and build
COPY . .
RUN npm run build

# Production stage with nginx
FROM nginx:alpine AS production

# Install dumb-init and security updates
RUN apk add --no-cache dumb-init && \
    apk update && apk upgrade && \
    rm -rf /var/cache/apk/*

# Copy built assets from build stage
COPY --from=build /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Create non-root user for nginx
RUN adduser -D -s /bin/sh nginxuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000 || exit 1

EXPOSE 3000

# Use dumb-init and run nginx
ENTRYPOINT ["dumb-init", "--"]
CMD ["nginx", "-g", "daemon off;"]