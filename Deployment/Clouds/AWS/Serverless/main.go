package main

import (
    "context"
    "fmt"
    "github.com/aws/aws-lambda-go/lambda"
)

type Request struct {
    Name string `json:"name"`
}

type Response struct {
    Message string `json:"message"`
}

func handler(ctx context.Context, name Request) (Response, error) {
    message := fmt.Sprintf("Hello, %s!", name.Name)
    return Response{Message: message}, nil
}

func main() {
    lambda.Start(handler)
}