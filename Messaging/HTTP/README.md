# HTTP

HTTP (HyperText Transfer Protocol) is used to transfer data across the Web.

HTTP is a protocol for fetching resources such as HTML documents. 

The net/http package provides the building blocks for writing an HTTP server. 

## How to implement HTTP server in Golang?

ListenAndServe starts an HTTP server with a given address and handler. 

The handler is usually nil, which means to use DefaultServeMux. 

Handle and HandleFunc add handlers to DefaultServeMux 

![alt text](https://github.com/jylhakos/InternetOfThings/blob/main/Messaging/HTTP/GET.png?raw=true)

Figure: HTTP Get reponse from the Golang.

## References

HTTP client and server implementations https://pkg.go.dev/net/http
