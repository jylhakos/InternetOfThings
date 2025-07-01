package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strings"

	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"

	authpb "auth-service/proto"
	productpb "product-service/proto"
	"microservices-go/pkg/discovery"
)

type Gateway struct {
	authClient    authpb.AuthServiceClient
	productClient productpb.ProductServiceClient
	registry      *discovery.EtcdRegistry
}

func NewGateway() (*Gateway, error) {
	registry, err := discovery.NewEtcdRegistry(
		[]string{"localhost:2379"},
		"/services",
		30,
	)
	if err != nil {
		return nil, err
	}

	// Connect to auth service
	authConn, err := connectToService(registry, "auth-service")
	if err != nil {
		return nil, fmt.Errorf("failed to connect to auth service: %v", err)
	}

	// Connect to product service
	productConn, err := connectToService(registry, "product-service")
	if err != nil {
		return nil, fmt.Errorf("failed to connect to product service: %v", err)
	}

	return &Gateway{
		authClient:    authpb.NewAuthServiceClient(authConn),
		productClient: productpb.NewProductServiceClient(productConn),
		registry:      registry,
	}, nil
}

func connectToService(registry *discovery.EtcdRegistry, serviceName string) (*grpc.ClientConn, error) {
	services, err := registry.Discover(serviceName)
	if err != nil {
		return nil, err
	}

	if len(services) == 0 {
		return nil, fmt.Errorf("no instances found for service %s", serviceName)
	}

	// Use the first available service instance
	service := services[0]
	addr := fmt.Sprintf("%s:%d", service.Address, service.Port)

	conn, err := grpc.Dial(addr, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		return nil, err
	}

	return conn, nil
}

func (g *Gateway) authenticateRequest(r *http.Request) (string, error) {
	authHeader := r.Header.Get("Authorization")
	if authHeader == "" {
		return "", fmt.Errorf("authorization header missing")
	}

	token := strings.TrimPrefix(authHeader, "Bearer ")
	if token == authHeader {
		return "", fmt.Errorf("invalid authorization header format")
	}

	resp, err := g.authClient.ValidateToken(context.Background(), &authpb.ValidateTokenRequest{
		Token: token,
	})
	if err != nil {
		return "", err
	}

	if !resp.Valid {
		return "", fmt.Errorf("invalid token")
	}

	return resp.UserId, nil
}

func (g *Gateway) handleGetProducts(w http.ResponseWriter, r *http.Request) {
	// Authenticate request
	if _, err := g.authenticateRequest(r); err != nil {
		http.Error(w, err.Error(), http.StatusUnauthorized)
		return
	}

	// Call product service
	resp, err := g.productClient.GetProducts(context.Background(), &emptypb.Empty{})
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(resp.Products)
}

func (g *Gateway) handleGetProduct(w http.ResponseWriter, r *http.Request) {
	// Authenticate request
	if _, err := g.authenticateRequest(r); err != nil {
		http.Error(w, err.Error(), http.StatusUnauthorized)
		return
	}

	// Extract product ID from URL
	productID := strings.TrimPrefix(r.URL.Path, "/api/products/")
	if productID == "" {
		http.Error(w, "product ID is required", http.StatusBadRequest)
		return
	}

	// Call product service
	resp, err := g.productClient.GetProduct(context.Background(), &productpb.GetProductRequest{
		Id: productID,
	})
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(resp)
}

func main() {
	gateway, err := NewGateway()
	if err != nil {
		log.Fatalf("Failed to create gateway: %v", err)
	}

	http.HandleFunc("/api/products", gateway.handleGetProducts)
	http.HandleFunc("/api/products/", gateway.handleGetProduct)

	log.Println("API Gateway listening on :8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}