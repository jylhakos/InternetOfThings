# Multi-stage Dockerfile for Vite React + ASP.NET Core Application
# This Dockerfile demonstrates best practices for containerizing the application

# Stage 1: Build React application with Vite
FROM node:18-alpine AS react-build

WORKDIR /app/client

# Copy package files
COPY Client/package*.json ./

# Install dependencies with clean install
RUN npm ci --only=production

# Copy source code
COPY Client/ ./

# Build React application for production
RUN npm run build

# Stage 2: Build ASP.NET Core application
FROM mcr.microsoft.com/dotnet/sdk:8.0-alpine AS dotnet-build

WORKDIR /app/server

# Copy csproj and restore dependencies
COPY Server/*.csproj ./
RUN dotnet restore

# Copy source code
COPY Server/ ./

# Build application
RUN dotnet publish -c Release -o /app/publish --no-restore

# Stage 3: Runtime image
FROM mcr.microsoft.com/dotnet/aspnet:8.0-alpine AS runtime

# Install curl for health checks
RUN apk --no-cache add curl

# Create non-root user for security
RUN adduser -D -s /bin/sh appuser

WORKDIR /app

# Copy published backend application
COPY --from=dotnet-build /app/publish ./

# Copy React build output to wwwroot
COPY --from=react-build /app/client/dist ./wwwroot

# Change ownership to appuser
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8080

# Environment variables
ENV ASPNETCORE_ENVIRONMENT=Production
ENV ASPNETCORE_URLS=http://+:8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Set entry point
ENTRYPOINT ["dotnet", "ViteReactASP.Server.dll"]
