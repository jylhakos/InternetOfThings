package main

import (
	"context"
	"fmt"
	"github.com/aws/aws-lambda-go/lambda"
	"github.com/aws/aws-lambda-go/events"
)

type Response struct {
	Message string `json:"message"`
}

func Handler(ctx context.Context, request events.APIGatewayProxyRequest) (events.APIGatewayProxyResponse, error) {

	message := fmt.Sprintf("Your request was processed with path: %s", request.Path)

	response := Response{
		Message: message,
	}

	return events.APIGatewayProxyResponse{
		Body:       fmt.Sprintf("%v", response),
		StatusCode: 200,
	}, nil
}

func main() {
	lambda.Start(Handler)
}