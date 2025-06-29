# Go

 To create a Docker container for a Go application that uses a PostgreSQL database for RESTful APIs, a multi-stage Dockerfile is recommended to ensure a small and efficient final image. Additionally, a docker-compose.yml file is beneficial for orchestrating both the Go application and the PostgreSQL database containers.

 Configure the necessary components to launch a Go application and PostgreSQL database using Docker.

- Multi-stage build reduces final image size

- Health checks ensures database is ready before starting API

- Environment variables for configuration management

- A non-root user is Docker security best practices

- Volume persistence that the database data survives container restarts

- Network isolation while services communicate through Docker network

- Alpine Linux is minimal base image for security and size

## A sample Go application providing RESTful APIs

```

    package main

    import (
        "database/sql"
        "encoding/json"
        "fmt"
        "log"
        "net/http"
        "os"

        "github.com/gorilla/mux"
        _ "github.com/lib/pq"
    )

    type App struct {
        Router *mux.Router
        DB     *sql.DB
    }

    func (a *App) Initialize() {
        var err error
        
        // Database connection string from environment variables
        dbHost := os.Getenv("DB_HOST")
        dbPort := os.Getenv("DB_PORT")
        dbUser := os.Getenv("DB_USER")
        dbPassword := os.Getenv("DB_PASSWORD")
        dbName := os.Getenv("DB_NAME")

        connectionString := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=disable",
            dbHost, dbPort, dbUser, dbPassword, dbName)

        a.DB, err = sql.Open("postgres", connectionString)
        if err != nil {
            log.Fatal("Failed to connect to database:", err)
        }

        if err = a.DB.Ping(); err != nil {
            log.Fatal("Failed to ping database:", err)
        }

        a.Router = mux.NewRouter()
        a.setRoutes()
    }

    func (a *App) setRoutes() {
        a.Router.HandleFunc("/api/health", a.healthCheck).Methods("GET")
        // Add your API routes here
    }

    func (a *App) healthCheck(w http.ResponseWriter, r *http.Request) {
        w.Header().Set("Content-Type", "application/json")
        json.NewEncoder(w).Encode(map[string]string{"status": "healthy"})
    }

    func (a *App) Run() {
        port := os.Getenv("API_PORT")
        if port == "" {
            port = "8080"
        }
        
        log.Printf("Server starting on port %s", port)
        log.Fatal(http.ListenAndServe(":"+port, a.Router))
    }

    func main() {
        app := &App{}
        app.Initialize()
        app.Run()
    }

```

The Go module files

```

    module your-app-name

    go 1.21

    require (
        github.com/gorilla/mux v1.8.0
        github.com/lib/pq v1.10.9
    )

```

SQL scripts to initialize PostgreSQL database

```

    -- Create tables and initial data
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Insert sample data
    INSERT INTO users (name, email) VALUES 
        ('John Doe', 'john@example.com'),
        ('Jane Smith', 'jane@example.com');

```

## Dockerizing a Go application

A typical Dockerfile for a Go application using a PostgreSQL database would involve next definitions.

Builder stage:

FROM golang:alpine AS builder: Use a Go image as the base for building the application. Alpine is preferred for smaller image size.

WORKDIR /app: Set the working directory inside the container.

COPY go.mod go.sum ./: Copy the Go module files to manage dependencies.

RUN go mod download: Download the Go module dependencies.

COPY . .: Copy the entire Go application source code.

RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main .: Build the Go application, disabling CGO for static compilation and creating a main executable.

Final stage:

FROM alpine:latest: Use a minimal Alpine image for the final production image.

WORKDIR /app: Set the working directory.

COPY --from=builder /app/main .: Copy the compiled Go executable from the builder stage.

EXPOSE 8080: Expose the port your Go API listens on (e.g., 8080).

CMD ["./main"]: Define the command to run the Go application when the container starts.

```

    # Use a multi-stage build for smaller images
    FROM golang:1.22-alpine AS builder

    WORKDIR /app

    # Copy go.mod and go.sum and download dependencies
    COPY go.mod go.sum ./
    RUN go mod download

    # Copy the rest of the application code
    COPY . .

    # Build the Go application
    RUN CGO_ENABLED=0 GOOS=linux go build -o main .

    # Final stage for a lean image
    FROM alpine:latest

    WORKDIR /app

    # Copy the built executable from the builder stage
    COPY --from=builder /app/main .

    # Expose the port your Go application listens on (e.g., 8080)
    EXPOSE 8080

    # Command to run the application
    CMD ["./main"]

```
Build the Docker image.

```

    $ docker build -t my-go-app .

```

## Dockerizing the database

Choose a database image: 

Use an official image from Docker Hub (e.g., postgres, mysql, mongo).

Create a Dockerfile: 

```

    FROM postgres:16-alpine

    # Copy SQL scripts for initial data or schema
    COPY init.sql /docker-entrypoint-initdb.d/

```
You might not need a separate Dockerfile for the database, as you can directly use the official image. 

Build the Docker image if you created a custom Dockerfile.

```

    $ docker build -t my-database .

```
### Orchestrating the Docker Containers with Docker Compose

A docker-compose.yml file can be used to define and link both the Go application and PostgreSQL database services:

Steps to create and run:

Create the Dockerfile: 

in your Go project's root directory.

```

    # Multi-stage build for optimal image size
    FROM golang:1.21-alpine AS builder

    # Install git for dependency management
    RUN apk add --no-cache git

    # Set working directory
    WORKDIR /app

    # Copy go mod files first for better caching
    COPY go.mod go.sum ./

    # Download dependencies
    RUN go mod download

    # Copy source code
    COPY . .

    # Build the application
    RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main .

    # Final stage - minimal runtime image
    FROM alpine:latest

    # Install ca-certificates for HTTPS requests
    RUN apk --no-cache add ca-certificates tzdata

    # Create non-root user for security
    RUN adduser -D -s /bin/sh appuser

    WORKDIR /root/

    # Copy the binary from builder stage
    COPY --from=builder /app/main .

    # Change ownership to non-root user
    RUN chown appuser:appuser main

    # Switch to non-root user
    USER appuser

    # Expose port (adjust based on your app)
    EXPOSE 8080

    # Run the binary
    CMD ["./main"]

```
Create the docker-compose.yml file: in the same root directory.

```

    version: '3.8'

    services:
      go-app:
        build: . # Build the Go application using the Dockerfile in the current directory
        ports:
          - "8080:8080" # Map host port 8080 to container port 8080
        environment:
          DATABASE_URL: "postgres://user:password@db:5432/mydatabase?sslmode=disable" # Connection string for PostgreSQL
        depends_on:
          - db # Ensure the database service starts before the Go application

      db:
        image: postgres:13-alpine # Use the official PostgreSQL image
        environment:
          POSTGRES_DB: mydatabase
          POSTGRES_USER: user
          POSTGRES_PASSWORD: password
        volumes:
          - pgdata:/var/lib/postgresql/data # Persist PostgreSQL data

    volumes:
      pgdata:

```

Run with Docker Compose command.

```

    $ docker-compose up -d

```

Build and run the containers: 

Open a terminal in the project root and execute docker-compose up --build. 

The docker-compose up --build command will build the Go application image, pull the PostgreSQL image, and start both containers.

```

    # Start all services
    docker-compose up --build

    # Run in background
    docker-compose up -d --build

    # View logs
    docker-compose logs -f api

    # Stop services
    docker-compose down

    # Remove volumes (careful - this deletes data)
    docker-compose down -v

```

Instead, create the Docker image using Docker commands.

```

    # Build the image
    $ docker build -t my-go-api .

    # Run with Docker network
    $ docker network create app-network

    $ docker run -d --name postgres --network app-network -e POSTGRES_PASSWORD=password postgres:15-alpine

    $ docker run -d --name api --network app-network -p 8080:8080 my-go-api

```

The .env file holds essential configurations and secrets for deploying servers and applications.

```

    # Database Configuration
    DB_HOST=postgres
    DB_PORT=5432
    DB_USER=postgres
    DB_PASSWORD=password
    DB_NAME=myapp

    # API Configuration
    API_PORT=8080
    API_HOST=0.0.0.0

    # Other configurations
    JWT_SECRET=your-secret-key
    LOG_LEVEL=info

```
The Docker ignore file to exclude files from the Docker image

```

    .git
    .gitignore
    README.md
    Dockerfile
    docker-compose.yml
    .env
    .env.local
    .env.*.local
    node_modules
    npm-debug.log*

```

Testing the Go application and PostgreSQL database

```

    # Test health endpoint
    $ curl http://localhost:8080/api/health

    # Check if PostgreSQL is accessible
    $ docker exec -it postgres_db psql -U postgres -d myapp -c "SELECT * FROM users;"

```

References

Use containers for Go development

https://docs.docker.com/guides/golang/develop/