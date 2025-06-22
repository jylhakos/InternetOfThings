# Java Spring Boot application on Docker

Deploying a Java Spring Boot web application for RESTful API services with a PostgreSQL database on Docker involves containerizing both the Spring Boot application and the PostgreSQL database, typically using Docker Compose for orchestration.

The setup provides a scalable, and production-ready Spring Boot REST API with PostgreSQL using Docker containers.

Multi-stage build to create optimized image size

Security to use non-root user, health checks

Environment separation to run different profiles for local or Docker

Health monitoring with actuator endpoints

Data persistence on PostgreSQL volumes

Automatic restarts defined for Docker container restart policies

Network isolation uses custom Docker network

Input validation with Spring Boot functions

Logging and monitoring

Set up a Spring Boot application with Spring Initializr

Navigate to https://start.spring.io. 

Spring Boot service pulls in all the dependencies you need for an application and does most of the setup for you.

The Java class is flagged as a @SpringBootApplication and as a @RestController, meaning that it is ready for use by Spring MVC to handle web requests.

You can continue with a Dockerfile for Maven.

```

	# Multi-stage build for optimal image size and security
	FROM maven:3.9.6-eclipse-temurin-21 AS builder

	# Set working directory
	WORKDIR /app

	# Copy Maven files for dependency caching
	COPY pom.xml .

	COPY src ./src

	# Build the application
	RUN mvn clean package -DskipTests

	# Runtime stage - use JRE instead of full JDK
	FROM eclipse-temurin:21-jre-alpine

	# Create non-root user for security
	RUN addgroup -g 1001 -S spring && \
	    adduser -u 1001 -S spring -G spring

	# Set working directory
	WORKDIR /app

	# Copy the JAR file from builder stage
	COPY --from=builder /app/target/*.jar app.jar

	# Change ownership to spring user
	RUN chown -R spring:spring /app

	# Switch to non-root user
	USER spring

	# Expose the application port
	EXPOSE 8080

	# Add health check
	HEALTHCHECK --interval=30s --timeout=3s --start-period=60s --retries=3 \
	    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/actuator/health || exit 1

	# Run the application
	ENTRYPOINT ["java", "-jar", "/app/app.jar"]

```

Alternative Dockerfile with Gradle

```

	# Multi-stage build for Gradle projects
	FROM gradle:8.5-jdk21 AS builder

	WORKDIR /app

	# Copy Gradle files for dependency caching
	COPY build.gradle settings.gradle ./

	COPY gradle ./gradle

	# Download dependencies
	RUN gradle dependencies --no-daemon

	# Copy source code and build
	COPY src ./src

	RUN gradle build --no-daemon -x test

	# Runtime stage
	FROM eclipse-temurin:21-jre-alpine

	RUN addgroup -g 1001 -S spring && \
	    adduser -u 1001 -S spring -G spring

	WORKDIR /app

	COPY --from=builder /app/build/libs/*.jar app.jar

	RUN chown -R spring:spring /app

	USER spring

	EXPOSE 8080

	HEALTHCHECK --interval=30s --timeout=3s --start-period=60s --retries=3 \
	    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/actuator/health || exit 1

	ENTRYPOINT ["java", "-jar", "/app/app.jar"]

```

Docker has a Dockerfile file format that it uses to specify the layers of an image.

Docker Compose 

```

	version: '3.8'

	services:
	  # PostgreSQL database
	  postgres:
	    image: postgres:16-alpine
	    container_name: postgres_db
	    restart: unless-stopped
	    environment:
	      POSTGRES_DB: springbootdb
	      POSTGRES_USER: postgres
	      POSTGRES_PASSWORD: password
	      POSTGRES_HOST_AUTH_METHOD: trust
	    ports:
	      - "5432:5432"
	    volumes:
	      - postgres_data:/var/lib/postgresql/data
	      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
	    networks:
	      - spring-network
	    healthcheck:
	      test: ["CMD-SHELL", "pg_isready -U postgres"]
	      interval: 30s
	      timeout: 10s
	      retries: 5
	      start_period: 30s

	  # Spring Boot application
	  app:
	    build:
	      context: .
	      dockerfile: Dockerfile
	    container_name: spring_boot_app
	    restart: unless-stopped
	    ports:
	      - "8080:8080"
	    environment:
	      - SPRING_PROFILES_ACTIVE=docker
	      - SPRING_DATASOURCE_URL=jdbc:postgresql://postgres:5432/springbootdb
	      - SPRING_DATASOURCE_USERNAME=postgres
	      - SPRING_DATASOURCE_PASSWORD=password
	      - SPRING_JPA_HIBERNATE_DDL_AUTO=update
	      - SPRING_JPA_DATABASE_PLATFORM=org.hibernate.dialect.PostgreSQLDialect
	      - SPRING_JPA_SHOW_SQL=true
	      - SERVER_PORT=8080
	    depends_on:
	      postgres:
	        condition: service_healthy
	    networks:
	      - spring-network
	    healthcheck:
	      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:8080/actuator/health"]
	      interval: 30s
	      timeout: 10s
	      retries: 3
	      start_period: 60s

	volumes:
	  postgres_data:

	networks:
	  spring-network:
	    driver: bridge

```

Spring Boot configuration for the application 

```

	# Default profile
	spring.application.name=spring-boot-postgres-api
	server.port=8080

	# Database configuration for local development
	spring.datasource.url=jdbc:postgresql://localhost:5432/springbootdb
	spring.datasource.username=postgres
	spring.datasource.password=password
	spring.datasource.driver-class-name=org.postgresql.Driver

	# JPA/Hibernate properties
	spring.jpa.database-platform=org.hibernate.dialect.PostgreSQLDialect
	spring.jpa.hibernate.ddl-auto=update
	spring.jpa.show-sql=true
	spring.jpa.properties.hibernate.format_sql=true

	# Actuator endpoints for health checks
	management.endpoints.web.exposure.include=health,info
	management.endpoint.health.show-details=always

```
Spring Boot configuration for Docker 

```

	# Docker profile configuration
	spring.datasource.url=jdbc:postgresql://postgres:5432/springbootdb
	spring.datasource.username=postgres
	spring.datasource.password=password

	# JPA settings for Docker
	spring.jpa.hibernate.ddl-auto=update
	spring.jpa.show-sql=false
	spring.jpa.properties.hibernate.format_sql=false

	# Logging
	logging.level.com.yourpackage=INFO
	logging.level.org.springframework.web=INFO

```
SQL script to initialize a database

```

	-- Create users table if it doesn't exist
	CREATE TABLE IF NOT EXISTS users (
	    id BIGSERIAL PRIMARY KEY,
	    name VARCHAR(255) NOT NULL,
	    email VARCHAR(255) UNIQUE NOT NULL,
	    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	);

	-- Insert sample data
	INSERT INTO users (name, email) VALUES 
	    ('John Doe', 'john.doe@example.com'),
	    ('Jane Smith', 'jane.smith@example.com'),
	    ('Bob Johnson', 'bob.johnson@example.com')
	ON CONFLICT (email) DO NOTHING;

```

The environment variables in .env file

```

	# Database Configuration
	POSTGRES_DB=springbootdb
	POSTGRES_USER=postgres
	POSTGRES_PASSWORD=password

	# Application Configuration
	SPRING_PROFILES_ACTIVE=docker
	SERVER_PORT=8080

	# JPA Configuration
	SPRING_JPA_HIBERNATE_DDL_AUTO=update
	SPRING_JPA_SHOW_SQL=false

```

A bash script to build Docker images

```

	#!/bin/bash

	# Build and run the application
	echo "Building and starting the application..."

	# Clean up existing containers and volumes (optional)
	# docker-compose down -v

	# Build and start services
	docker-compose up --build -d

	# Wait for services to be ready
	echo "Waiting for services to start..."
	sleep 30

	# Check if services are running
	docker-compose ps

	# Test the API
	echo "Testing the API..."
	curl -X GET http://localhost:8080/api/users
	curl -X GET http://localhost:8080/actuator/health

	echo "Deployment complete!"
	echo "API is available at: http://localhost:8080/api/users"
	echo "Health check at: http://localhost:8080/actuator/health"

```
References

Spring Boot with Docker

https://spring.io/guides/gs/spring-boot-docker
