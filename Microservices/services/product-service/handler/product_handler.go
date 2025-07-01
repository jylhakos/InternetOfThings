package handler

import (
	"context"
	"fmt"
	"time"

	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
	"google.golang.org/protobuf/types/known/emptypb"

	pb "product-service/proto"
)

type ProductHandler struct {
	pb.UnimplementedProductServiceServer
	// In a real application, you'd inject a repository here
	products map[string]*pb.Product
}

func NewProductHandler() *ProductHandler {
	return &ProductHandler{
		products: make(map[string]*pb.Product),
	}
}

func (h *ProductHandler) GetProduct(ctx context.Context, req *pb.GetProductRequest) (*pb.Product, error) {
	if req.Id == "" {
		return nil, status.Error(codes.InvalidArgument, "product ID is required")
	}

	product, exists := h.products[req.Id]
	if !exists {
		return nil, status.Error(codes.NotFound, "product not found")
	}

	return product, nil
}

func (h *ProductHandler) GetProducts(ctx context.Context, req *emptypb.Empty) (*pb.ProductList, error) {
	var products []*pb.Product
	for _, product := range h.products {
		products = append(products, product)
	}

	return &pb.ProductList{Products: products}, nil
}

func (h *ProductHandler) CreateProduct(ctx context.Context, req *pb.CreateProductRequest) (*pb.Product, error) {
	if req.Name == "" {
		return nil, status.Error(codes.InvalidArgument, "product name is required")
	}

	id := fmt.Sprintf("prod_%d", time.Now().Unix())
	now := time.Now().Unix()

	product := &pb.Product{
		Id:          id,
		Name:        req.Name,
		Description: req.Description,
		Price:       req.Price,
		Stock:       req.Stock,
		Category:    req.Category,
		CreatedAt:   now,
		UpdatedAt:   now,
	}

	h.products[id] = product
	return product, nil
}

func (h *ProductHandler) UpdateProduct(ctx context.Context, req *pb.UpdateProductRequest) (*pb.Product, error) {
	if req.Id == "" {
		return nil, status.Error(codes.InvalidArgument, "product ID is required")
	}

	product, exists := h.products[req.Id]
	if !exists {
		return nil, status.Error(codes.NotFound, "product not found")
	}

	// Update fields
	if req.Name != "" {
		product.Name = req.Name
	}
	if req.Description != "" {
		product.Description = req.Description
	}
	if req.Price > 0 {
		product.Price = req.Price
	}
	if req.Stock >= 0 {
		product.Stock = req.Stock
	}
	if req.Category != "" {
		product.Category = req.Category
	}
	product.UpdatedAt = time.Now().Unix()

	h.products[req.Id] = product
	return product, nil
}

func (h *ProductHandler) DeleteProduct(ctx context.Context, req *pb.DeleteProductRequest) (*emptypb.Empty, error) {
	if req.Id == "" {
		return nil, status.Error(codes.InvalidArgument, "product ID is required")
	}

	_, exists := h.products[req.Id]
	if !exists {
		return nil, status.Error(codes.NotFound, "product not found")
	}

	delete(h.products, req.Id)
	return &emptypb.Empty{}, nil
}