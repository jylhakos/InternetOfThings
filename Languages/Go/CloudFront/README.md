# Example: Go program and React application

This is typically achieved in two ways.

In both scenarios, the core interaction between the React application and Go program relies on HTTP requests and responses, with data typically exchanged in JSON format.

1. Go back-end serving static files for React application directly

By serving as a web server and sending the compiled React static files to the client's browser, a Go program can be used as the back-end for a React application.

The React application is built into static assets (HTML, CSS, JavaScript files) using a command like npm run build or yarn build.

This creates a build or dist directory containing the optimized production-ready files.

The Go program is configured to serve these static files from a specific directory.

This is commonly done using Go's http.FileServer and http.StripPrefix functions.

When a request comes in for the root path or any path not handled by API routes, the Go server serves the index.html file of the React app, and the React router handles the client-side routing.

```

    package main

    import (
    	"log"
    	"net/http"
    )

    func main() {
    	// Serve static files from the 'build' directory (where React app is built)
    	fs := http.FileServer(http.Dir("./client/build"))

    	http.Handle("/", fs)

    	// Add API routes (example)
    	http.HandleFunc("/api/data", func(w http.ResponseWriter, r *http.Request) {
    		w.Write([]byte("Go API"))
    	})

    	log.Println("Server starting on port 8080.")

    	log.Fatal(http.ListenAndServe(":8080", nil))
    }

 ```
2. Go back-end with APIs for React application with separate web server hosting

In this approach, the Go program exclusively functions as an API interface, handling data requests and business logic.

The React application is deployed and served separately, for example, using a dedicated web server like Nginx, Apache, or a static site hosting service.

The React application then makes HTTP requests (e.g., using fetch or axios) to the Go backend's API endpoints to retrieve and send data. 

Cross-Origin Resource Sharing (CORS) must be configured on the Go program to allow requests from the React app's domain.

# Example: Go program uploads the static assets to S3 and React application utilizes AWS CloudFront

Go program can interact with AWS S3 for uploading static files and integrate with CloudFront for serving them efficiently for a React application.

1. Go program to upload static files to S3

To upload files, the Go program utilizes the AWS SDK for Go.

The Go program's role is specifically for automating the upload process to S3.

Install AWS SDK for Go.

```

    $ go get github.com/aws/aws-sdk-go/aws

    $ go get github.com/aws/aws-sdk-go/aws/session

    $ go get github.com/aws/aws-sdk-go/service/s3/s3manager

```
AWS S3 configuration

Create an S3 Bucket: 

Create a new S3 bucket in your desired AWS region.

Enable Static Website Hosting:

In the bucket properties, enable "Static website hosting" and specify index.html as the index document and potentially an error document (e.g., error.html).

Configure Bucket Policy:

Set a bucket policy that grants public read access to the objects within the bucket, or more securely, restrict access to only your CloudFront distribution using an Origin Access Control (OAC) or Origin Access Identity (OAI).

AWS CloudFront configuration

Create a CloudFront Distribution: Create a new web distribution.

Set Origin: 

Select your S3 bucket as the origin domain.

Configure Cache behavior: 

Define cache behaviors for different file types (e.g., HTML, CSS, JS, images) to optimize caching and performance.

SSL/TLS certificate: 

Configure an SSL/TLS certificate for HTTPS access (e.g., using AWS Certificate Manager).

Default root object: 

Set index.html as the default root object.

Origin access: 

If using OAC/OAI, ensure CloudFront is configured to use it for secure access to the S3 bucket.

Build the React application: 

Use npm run build or yarn build to create a production build of your React application. 

```

	$ npm run build

```
This will generate static files (HTML, CSS, JS, etc.) in a build directory for React application.

Run the Go program

```

	package main

    import (
    	"fmt"
    	"os"
    	"path/filepath"

    	"github.com/aws/aws-sdk-go/aws"
    	"github.com/aws/aws-sdk-go/aws/session"
    	"github.com/aws/aws-sdk-go/service/s3/s3manager"
    )

    func main() {
    	bucketName := "your-s3-bucket-name"
    	// Path to your React app's build directory
    	buildPath := "./build" 

    	sess, err := session.NewSession(&aws.Config{
    		Region: aws.String("your-aws-region"), // e.g., "us-east-1"
    	})
    	if err != nil {
    		fmt.Printf("Failed to create AWS session: %v\n", err)
    		return
    	}

    	uploader := s3manager.NewUploader(sess)

    	err = filepath.Walk(buildPath, func(path string, info os.FileInfo, err error) error {
    		if err != nil {
    			return fmt.Errorf("error walking path %q: %v", path, err)
    		}
    		if info.IsDir() {
    			return nil // Skip directories
    		}

    		relPath, err := filepath.Rel(buildPath, path)
    		if err != nil {
    			return fmt.Errorf("failed to get relative path: %v", err)
    		}

    		file, err := os.Open(path)
    		if err != nil {
    			return fmt.Errorf("failed to open file %q: %v", path, err)
    		}
    		defer file.Close()

    		_, err = uploader.Upload(&s3manager.UploadInput{
    			Bucket: aws.String(bucketName),
    			Key:    aws.String(relPath),
    			Body:   file,
    			// Set Content-Type based on file extension if needed
    			// ContentType: aws.String(mime.TypeByExtension(filepath.Ext(path))),
    		})
    		if err != nil {
    			return fmt.Errorf("failed to upload file %q: %v", relPath, err)
    		}
    		fmt.Printf("Uploaded %s to s3://%s/%s\n", path, bucketName, relPath)
    		return nil
    	})

    	if err != nil {
    		fmt.Printf("Error during file upload: %v\n", err)
    	} else {
    		fmt.Println("All static files uploaded successfully!")
    	}
    }

```
Execute the Go program to upload the contents of your React app's build directory to the configured S3 bucket.

2. Providing static files for React application via S3 and CloudFront

The Go program does not directly provide static files for the React application, instead Go program uploads the React application's build output (static files) to an S3 bucket configured for static website hosting.

CloudFront then acts as a CDN to serve these files globally.

Steps for S3 and CloudFront Setup (outside the Go program).

Build React application:

Run npm run build or yarn build in your React project to generate the build directory containing static files.

```

	$ npm run build

```

Create S3 bucket:

Create an S3 bucket and enable static website hosting in its properties. Configure the index document (e.g., index.html) and error document.

Upload files:

Use the Go program (above) to upload the contents of your React build directory to this S3 bucket.

Create CloudFront distribution:

Create a CloudFront distribution, pointing its origin to your S3 static website endpoint. Configure caching, SSL certificates, and other desired settings.

Configure bucket policy:

Ensure your S3 bucket policy allows CloudFront to access its contents. This typically involves allowing s3:GetObject action for the CloudFront OAI (Origin Access Identity) or OAC (Origin Access Control).

DNS configuration (Optional):

If using a custom domain, configure your DNS records (e.g., CNAME) to point to the CloudFront distribution's domain name.

Once these steps are completed, CloudFront will serve your React application's static files directly from S3, leveraging its global network for faster delivery. 

References

Deploy a React based single page application to Amazon S3 and CloudFront

https://docs.aws.amazon.com/prescriptive-guidance/latest/patterns/deploy-a-react-based-single-page-application-to-amazon-s3-and-cloudfront.html
