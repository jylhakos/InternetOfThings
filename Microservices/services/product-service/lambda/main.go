package main

import (
	"context"
	"encoding/json"

	"github.com/aws/aws-lambda-go/events"
	"github.com/aws/aws-lambda-go/lambda"
	
	"product-service/handler"
	pb "product-service/proto"
)

type LambdaHandler struct {
	productHandler *handler.ProductHandler
}

func (h *LambdaHandler) HandleRequest(ctx context.Context, request events.APIGatewayProxyRequest) (events.APIGatewayProxyResponse, error) {
	switch request.HTTPMethod {
	case "GET":
		if request.PathParameters["id"] != "" {
			return h.getProduct(ctx, request.PathParameters["id"])
		}
		return h.getProducts(ctx)
	case "POST":
		return h.createProduct(ctx, request.Body)
	case "PUT":
		return h.updateProduct(ctx, request.PathParameters["id"], request.Body)
	case "DELETE":
		return h.deleteProduct(ctx, request.PathParameters["id"])
	default:
		return events.APIGatewayProxyResponse{
			StatusCode: 405,
			Body:       "Method not allowed",
		}, nil
	}
}

func (h *LambdaHandler) getProduct(ctx context.Context, id string) (events.APIGatewayProxyResponse, error) {
	product, err := h.productHandler.GetProduct(ctx, &pb.GetProductRequest{Id: id})
	if err != nil {
		return events.APIGatewayProxyResponse{
			StatusCode: 500,
			Body:       err.Error(),
		}, nil
	}

	body, _ := json.Marshal(product)
	return events.APIGatewayProxyResponse{
		StatusCode: 200,
		Headers:    map[string]string{"Content-Type": "application/json"},
		Body:       string(body),
	}, nil
}

func main() {
	handler := &LambdaHandler{
		productHandler: handler.NewProductHandler(),
	}
	lambda.Start(handler.HandleRequest)
}