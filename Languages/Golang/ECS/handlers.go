package main

import (
	"database/sql"
	"encoding/json"
	"net/http"

	"github.com/gorilla/mux"
)

func getItems(w http.ResponseWriter, r *http.Request) {
	rows, err := db.Query("SELECT id, name, value FROM items")
	if err != nil {
		http.Error(w, err.Error(), 500)
		return
	}
	defer rows.Close()
	var items []Item
	for rows.Next() {
		var i Item
		if err := rows.Scan(&i.ID, &i.Name, &i.Value); err != nil {
			http.Error(w, err.Error(), 500)
			return
		}
		items = append(items, i)
	}
	json.NewEncoder(w).Encode(items)
}

func getItem(w http.ResponseWriter, r *http.Request) {
	id := mux.Vars(r)["id"]
	var i Item
	err := db.QueryRow("SELECT id, name, value FROM items WHERE id=$1", id).Scan(&i.ID, &i.Name, &i.Value)
	if err == sql.ErrNoRows {
		http.NotFound(w, r)
		return
	} else if err != nil {
		http.Error(w, err.Error(), 500)
		return
	}
	json.NewEncoder(w).Encode(i)
}

func createItem(w http.ResponseWriter, r *http.Request) {
	var i Item
	if err := json.NewDecoder(r.Body).Decode(&i); err != nil {
		http.Error(w, err.Error(), 400)
		return
	}
	err := db.QueryRow("INSERT INTO items(name, value) VALUES($1, $2) RETURNING id", i.Name, i.Value).Scan(&i.ID)
	if err != nil {
		http.Error(w, err.Error(), 500)
		return
	}
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(i)
}

func updateItem(w http.ResponseWriter, r *http.Request) {
	id := mux.Vars(r)["id"]
	var i Item
	if err := json.NewDecoder(r.Body).Decode(&i); err != nil {
		http.Error(w, err.Error(), 400)
		return
	}
	_, err := db.Exec("UPDATE items SET name=$1, value=$2 WHERE id=$3", i.Name, i.Value, id)
	if err != nil {
		http.Error(w, err.Error(), 500)
		return
	}
	w.WriteHeader(http.StatusNoContent)
}

func deleteItem(w http.ResponseWriter, r *http.Request) {
	id := mux.Vars(r)["id"]
	_, err := db.Exec("DELETE FROM items WHERE id=$1", id)
	if err != nil {
		http.Error(w, err.Error(), 500)
		return
	}
	w.WriteHeader(http.StatusNoContent)
}
