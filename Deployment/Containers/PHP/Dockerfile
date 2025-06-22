# Multi-stage build for PHP REST API
FROM php:8.3-fpm-alpine AS base

# Install system dependencies
RUN apk add --no-cache \
    curl \
    libpng-dev \
    oniguruma-dev \
    libxml2-dev \
    zip \
    unzip \
    git \
    nginx \
    supervisor

# Install PHP extensions
RUN docker-php-ext-install \
    pdo_mysql \
    mbstring \
    exif \
    pcntl \
    bcmath \
    gd \
    opcache

# Install Composer
COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

# Create non-root user
RUN addgroup -g 1001 -S www && \
    adduser -u 1001 -S www -G www

# Set working directory
WORKDIR /var/www/html

# Development stage
FROM base AS development

# Copy PHP development configuration
COPY docker/php/php-dev.ini /usr/local/etc/php/conf.d/99-custom.ini

# Install development dependencies
RUN apk add --no-cache \
    xdebug

# Enable Xdebug
RUN docker-php-ext-enable xdebug

# Copy source code
COPY --chown=www:www . .

# Install Composer dependencies
RUN composer install --no-cache

USER www
EXPOSE 9000
CMD ["php-fpm"]

# Production stage
FROM base AS production

# Copy PHP production configuration
COPY docker/php/php-prod.ini /usr/local/etc/php/conf.d/99-custom.ini
COPY docker/php/opcache.ini /usr/local/etc/php/conf.d/opcache.ini

# Copy Nginx configuration
COPY docker/nginx/nginx.conf /etc/nginx/nginx.conf
COPY docker/nginx/default.conf /etc/nginx/http.d/default.conf

# Copy Supervisor configuration
COPY docker/supervisor/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Copy source code
COPY --chown=www:www . .

# Install production dependencies
RUN composer install --no-dev --optimize-autoloader --no-cache

# Create required directories
RUN mkdir -p /var/log/supervisor /var/log/nginx /var/log/php-fpm

# Set permissions
RUN chown -R www:www /var/www/html /var/log/nginx /var/log/php-fpm
RUN chmod -R 755 /var/www/html

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Expose port
EXPOSE 80

# Start supervisor
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]