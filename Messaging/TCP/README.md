# TCP/IP

The Transmission Control Protocol (TCP) is used as a host-to-host protocol between hosts in packet-switched computer communication networks.

TCP is a connection-oriented, end-to-end reliable protocol for a layered hierarchy of protocols which support multi-network applications.

The IP header contains the IP address, which builds a single logical network from multiple physical networks.

When A sends an IP packet to B, the IP header contains A's IP address as the source IP address, also, the IP header contains B's IP address as the destination IP address.

For an application that uses TCP, data passes between the application and the TCP module.

![alt text](https://github.com/jylhakos/InternetOfThings/blob/main/Messaging/TCP/layers.png?raw=true)

Figure: TCP/IP in the layered protocol architecture.

## How to implement TCP/IP server in Golang?

Golang net package provides an interface for network I/O, including TCP/IP, UDP, domain name resolution, and Unix domain sockets.

The Listen function creates a server and Accept waits for and returns the next connection to the listener.

ResolveTCPAddr returns an address of TCP end point for example localhost:80 or 127.0.0.1:80.

For TCP and UDP networks, the address has the form "host:port". 

The host must be a literal IP address, or a host name that can be resolved to IP addresses. 

The port must be a literal port number or a service name.

The DialTCP function connects to the remote address on the TCP networks.

A goroutine is a lightweight thread managed by the Go runtime and each incoming request is handled in its own goroutine.

## References

Go networking libraries https://github.com/golang/net

Goroutines https://go.dev/tour/concurrency/1