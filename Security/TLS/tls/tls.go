// $ openssl genrsa -out ca.key 4096
// $ openssl req -new -x509 -days 365 -key ca.key -out cert.pem -subj "/C=UK/ST=London/L=London/O=Golang/OU=org/CN=localhost"
// $ openssl genrsa -out private.key 4096
// $ openssl req -new -key private.key -out private.csr -subj "/C=UK/ST=London/L=London/O=Golang/OU=org/CN=computer"
// $ openssl x509 -req -in private.csr -CA cert.pem -CAkey ca.key -out private.crt -CAcreateserial -days 365 -sha256 -extfile ext.cnf
// $ cp private.crt certificate.pem
// $ cat cert.pem >> certificate.pem
// $ curl -k -X GET https://localhost:8443/api -v

package main

import (
	"fmt"
	"log"
	"net/http"
	"os"
)

var tlsCert = "../certs/certificate.pem"

var tlsKey = "../certs/private.key"

func homeHandler(res http.ResponseWriter, req *http.Request) {
	fmt.Fprintf(res, "Echo\n")
}

func apiHandler(w http.ResponseWriter, req *http.Request) {
	fmt.Fprintf(w, "HTTPS\n")
}

func healthCheckHandler(w http.ResponseWriter, req *http.Request) {
	fmt.Fprintf(w, "OK\n")
}

func setupHandlers(mux *http.ServeMux) {
	mux.HandleFunc("/healthz", healthCheckHandler)
	mux.HandleFunc("/api", apiHandler)
	mux.HandleFunc("/", homeHandler)
}

func main() {
	fmt.Println("main()")
	listenAddr := os.Getenv("LISTEN_ADDR")
	if len(listenAddr) == 0 {
		listenAddr = ":8443"
	}
	mux := http.NewServeMux()
	setupHandlers(mux)
	log.Fatal(http.ListenAndServeTLS(listenAddr, tlsCert, tlsKey, mux))
}