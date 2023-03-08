package main

import (
	"fmt"
	"log"
	"net/http"
	"os"
)

func apiHandler(w http.ResponseWriter, req *http.Request) {
	fmt.Fprintf(w, "Server\n")
}

func healthCheckHandler(w http.ResponseWriter, req *http.Request) {
	fmt.Fprintf(w, "OK\n")
}

func setupHandlers(mux *http.ServeMux) {
	mux.HandleFunc("/healthz", healthCheckHandler)
	mux.HandleFunc("/api", apiHandler)
}

func main() {
    fmt.Println("main()")
    listenAddr := os.Getenv("LISTEN_ADDR")
	if len(listenAddr) == 0 {
		listenAddr = ":8085"
	}
	mux := http.NewServeMux()
	setupHandlers(mux)
	log.Fatal(http.ListenAndServe(listenAddr, mux))
}