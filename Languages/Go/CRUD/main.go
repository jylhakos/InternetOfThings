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

type Item struct {
    ID    int    `json:"id"`
    Name  string `json:"name"`
    Value string `json:"value"`
}

var db *sql.DB

func main() {
    var err error
    db, err = sql.Open("postgres", os.Getenv("DATABASE_URL"))
    if err != nil {
        log.Fatal(err)
    }
    defer db.Close()

    r := mux.NewRouter()
    r.HandleFunc("/items", createItem).Methods("POST")
    r.HandleFunc("/items", getItems).Methods("GET")
    r.HandleFunc("/items/{id}", getItem).Methods("GET")
    r.HandleFunc("/items/{id}", updateItem).Methods("PUT")
    r.HandleFunc("/items/{id}", deleteItem).Methods("DELETE")

    log.Fatal(http.ListenAndServe(":8080", r))
}

func createItem(w http.ResponseWriter, r *http.Request) {
    var item Item
    json.NewDecoder(r.Body).Decode(&item)
    err := db.QueryRow("INSERT INTO items(name, value) VALUES($1, $2) RETURNING id", item.Name, item.Value).Scan(&item.ID)
    if err != nil {
        http.Error(w, err.Error(), http.StatusInternalServerError)
        return
    }
    json.NewEncoder(w).Encode(item)
}

func getItems(w http.ResponseWriter, r *http.Request) {
    rows, err := db.Query("SELECT id, name, value FROM items")
    if err != nil {
        http.Error(w, err.Error(), http.StatusInternalServerError)
        return
    }
    defer rows.Close()
    var items []Item
    for rows.Next() {
        var item Item
        rows.Scan(&item.ID, &item.Name, &item.Value)
        items = append(items, item)
    }
    json.NewEncoder(w).Encode(items)
}

func getItem(w http.ResponseWriter, r *http.Request) {
    id := mux.Vars(r)["id"]
    var item Item
    err := db.QueryRow("SELECT id, name, value FROM items WHERE id=$1", id).Scan(&item.ID, &item.Name, &item.Value)
    if err != nil {
        http.Error(w, err.Error(), http.StatusNotFound)
        return
    }
    json.NewEncoder(w).Encode(item)
}

func updateItem(w http.ResponseWriter, r *http.Request) {
    id := mux.Vars(r)["id"]
    var item Item
    json.NewDecoder(r.Body).Decode(&item)
    _, err := db.Exec("UPDATE items SET name=$1, value=$2 WHERE id=$3", item.Name, item.Value, id)
    if err != nil {
        http.Error(w, err.Error(), http.StatusInternalServerError)
        return
    }
    w.WriteHeader(http.StatusNoContent)
}

func deleteItem(w http.ResponseWriter, r *http.Request) {
    id := mux.Vars(r)["id"]
    _, err := db.Exec("DELETE FROM items WHERE id=$1", id)
    if err != nil {
        http.Error(w, err.Error(), http.StatusInternalServerError)
        return
    }
    w.WriteHeader(http.StatusNoContent)
}
