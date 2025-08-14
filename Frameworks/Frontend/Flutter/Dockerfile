# Multi-stage Flutter Web Build
FROM cirrusci/flutter:stable AS flutter-builder

# Set working directory
WORKDIR /app

# Copy pubspec files
COPY pubspec.yaml pubspec.lock ./

# Enable web support and get dependencies
RUN flutter config --enable-web
RUN flutter pub get

# Copy source code
COPY lib ./lib
COPY web ./web
COPY assets ./assets

# Build Flutter web app
RUN flutter build web --release --web-renderer html

# Production stage with Nginx
FROM nginx:alpine AS production

# Install curl for health checks
RUN apk add --no-cache curl

# Copy built Flutter web app
COPY --from=flutter-builder /app/build/web /usr/share/nginx/html

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Create nginx user and set permissions
RUN addgroup -g 1001 -S nginx && \
    adduser -D -S -u 1001 -G nginx nginx && \
    chown -R nginx:nginx /usr/share/nginx/html && \
    chown -R nginx:nginx /var/cache/nginx && \
    chown -R nginx:nginx /var/log/nginx && \
    chown -R nginx:nginx /etc/nginx/conf.d

# Switch to non-root user
USER nginx

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
