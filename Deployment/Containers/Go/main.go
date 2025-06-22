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