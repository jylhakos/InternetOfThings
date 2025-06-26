package main

import (
	"fmt"
	"os"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/s3/s3manager"
)

func main() {
	if len(os.Args) != 3 {
		exitErrorf("Usage: %s <bucket_name> <file_path>", os.Args[0])
	}

	bucketName := os.Args[1]
	filePath := os.Args[2]

	// Initialize a session with your AWS region
	sess, err := session.NewSession(&aws.Config{
		Region: aws.String("your-aws-region"), // e.g., "us-east-1"
	})
	if err != nil {
		exitErrorf("Failed to create AWS session, %v", err)
	}

	// Create an S3 Uploader
	uploader := s3manager.NewUploader(sess)

	// Open the file to upload
	file, err := os.Open(filePath)
	if err != nil {
		exitErrorf("Failed to open file %q, %v", filePath, err)
	}
	defer file.Close()

	// Upload the file to S3
	_, err = uploader.Upload(&s3manager.UploadInput{
		Bucket: aws.String(bucketName),
		Key:    aws.String(filePath), // Use file path as key in S3
		Body:   file,
	})
	if err != nil {
		exitErrorf("Failed to upload file to S3, %v", err)
	}

	fmt.Printf("Successfully uploaded %q to S3 bucket %q\n", filePath, bucketName)
}

func exitErrorf(msg string, args ...interface{}) {
	fmt.Fprintf(os.Stderr, msg+"\n", args...)
	os.Exit(1)
}
