package main

import (
    "database/sql"
    "encoding/json"
    "log"
    "net/http"
    "os"

    "github.com/gorilla/mux"
    _ "github.com/lib/pq"
)

type App struct {
    DB *sql.DB
}

func main() {
    app := &App{}
    app.Initialize()
    app.Run(":8080")
}

func (a *App) Initialize() {
    dbHost := os.Getenv("DB_HOST")
    dbUser := os.Getenv("DB_USER")
    dbPassword := os.Getenv("DB_PASSWORD")
    dbName := os.Getenv("DB_NAME")
    
    connectionString := fmt.Sprintf("host=%s user=%s password=%s dbname=%s sslmode=require", 
        dbHost, dbUser, dbPassword, dbName)
    
    var err error
    a.DB, err = sql.Open("postgres", connectionString)
    if err != nil {
        log.Fatal(err)
    }
}

func (a *App) Run(addr string) {
    router := mux.NewRouter()
    // Add your API routes here
    router.HandleFunc("/health", a.healthCheck).Methods("GET")
    
    log.Printf("Server starting on %s", addr)
    log.Fatal(http.ListenAndServe(addr, router))
}

func (a *App) healthCheck(w http.ResponseWriter, r *http.Request) {
    json.NewEncoder(w).Encode(map[string]string{"status": "healthy"})
}