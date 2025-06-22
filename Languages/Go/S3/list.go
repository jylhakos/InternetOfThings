package main

import (
    "context"
    "fmt"
    "log"

    "github.com/aws/aws-sdk-go-v2/aws"
    "github.com/aws/aws-sdk-go-v2/config"
    "github.com/aws/aws-sdk-go-v2/service/s3"
)

func main() {
    cfg, err := config.LoadDefaultConfig(context.TODO())
    if err != nil {
        log.Fatalf("Error: failed to load configuration, %v", err)
    }

    client := s3.NewFromConfig(cfg)

    result, err := client.ListBuckets(context.TODO(), &s3.ListBucketsInput{})
    if err != nil {
        log.Fatalf("Error: failed to list S3 buckets, %v", err)
    }

    fmt.Println("The S3 buckets:")
    for _, bucket := range result.Buckets {
        fmt.Printf("* %s\n", *bucket.Name)
    }
}