package main

import (
	"fmt"
	"net"
	"os"
)

const (
	HOST = "localhost"
	PORT = "8084"
	TYPE = "tcp"
)

func main() {
	fmt.Println("client")
	tcpServer, err := net.ResolveTCPAddr(TYPE, HOST+":"+PORT)

	if err != nil {
		println("Resolving TCP Address failed.", err.Error())
		os.Exit(1)
	}

	conn, err := net.DialTCP(TYPE, nil, tcpServer)

	if err != nil {
		println("Connecting to server failed.", err.Error())
		os.Exit(1)
	}

	_, err = conn.Write([]byte("GET"))

	if err != nil {
		println("Writing data failed.", err.Error())
		os.Exit(1)
	}

	received := make([]byte, 2048)

	_, err = conn.Read(received)

	if err != nil {
		println("Reading data failed.", err.Error())
		os.Exit(1)
	}

	println("Received", string(received))

	conn.Close()
}
