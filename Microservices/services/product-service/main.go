package main

import (
	"context"
	"fmt"
	"log"
	"net"
	"os"
	"os/signal"
	"syscall"

	"google.golang.org/grpc"
	"google.golang.org/grpc/reflection"

	pb "product-service/proto"
	"product-service/handler"
	"microservices-go/pkg/discovery"
)

func main() {
	port := os.Getenv("PORT")
	if port == "" {
		port = "50051"
	}

	// Create etcd registry
	registry, err := discovery.NewEtcdRegistry(
		[]string{"localhost:2379"}, // etcd endpoints
		"/services",                // prefix
		30,                         // TTL in seconds
	)
	if err != nil {
		log.Fatalf("Failed to create etcd registry: %v", err)
	}

	// Register service
	serviceInfo := discovery.ServiceInfo{
		Name:    "product-service",
		Address: "localhost",
		Port:    50051,
		Metadata: map[string]string{
			"version": "1.0.0",
		},
	}

	if err := registry.Register(context.Background(), serviceInfo); err != nil {
		log.Fatalf("Failed to register service: %v", err)
	}

	// Setup gRPC server
	lis, err := net.Listen("tcp", ":"+port)
	if err != nil {
		log.Fatalf("Failed to listen: %v", err)
	}

	s := grpc.NewServer()
	pb.RegisterProductServiceServer(s, &handler.ProductHandler{})
	
	// Enable reflection for debugging
	reflection.Register(s)

	log.Printf("Product service listening on port %s", port)

	// Graceful shutdown
	c := make(chan os.Signal, 1)
	signal.Notify(c, os.Interrupt, syscall.SIGTERM)

	go func() {
		<-c
		log.Println("Shutting down gRPC server...")
		registry.Deregister()
		s.GracefulStop()
	}()

	if err := s.Serve(lis); err != nil {
		log.Fatalf("Failed to serve: %v", err)
	}
}