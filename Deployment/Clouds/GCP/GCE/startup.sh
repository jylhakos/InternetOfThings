#!/bin/bash

# Create a directory for your application
mkdir /opt/go-app

cd /opt/go-app

# Copy your Go application binary to the instance (you'll need to upload it first)
gsutil cp gs://your-bucket-name/your-go-binary .

# Make the binary executable
chmod +x your-go-binary

# Run your application (replace with your app's startup command)
./your-go-binary