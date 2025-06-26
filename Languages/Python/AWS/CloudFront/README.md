# Providing static files for a React application using FastAPI program with AWS S3 and CloudFront

FastAPI program provides static files for a React application, which are then hosted using S3 and CloudFront on AWS.

Users access your React application through the CloudFront distribution URL, which serves the static files from S3.

FastAPI program can serve as your backend API, handling dynamic requests from the React application.

1. Setup FastAPI libraries for serving static files

Install FastAPI libraries and python-multipart by pip tool.

```

	$ pip install fastapi "uvicorn[standard]" python-multipart

```
Create a FastAPI program to serve React application.

```

    from fastapi import FastAPI
    from fastapi.staticfiles import StaticFiles

    app = FastAPI()

    # Mount the directory containing your React build (e.g., 'build' folder)
    app.mount("/static", StaticFiles(directory="path/to/your/react/build"), name="static")

    # Serve the index.html for your React single-page-application (SPA)
    @app.get("/")
    async def read_root():
        with open("path/to/your/react/build/index.html") as f:
            return f.read()

```
Replace "path/to/your/react/build" with the actual path to your React application's build directory after running npm run build.

2. AWS S3 sonfiguration for Static Website Hosting

Create an S3 bucket: 

In the AWS S3 console, create a new bucket. 

Choose a unique name.

Enable Static Website Hosting: 

In the bucket properties, enable "Static website hosting" and specify index.html as both the Index document and Error document.

Set bucket policy:

Configure a bucket policy to allow public read access to your static files.

```

    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "PublicReadGetObject",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": "arn:aws:s3:::your-bucket-name/*"
            }
        ]
    }

```

Replace your-bucket-name with your actual S3 bucket name.

3. AWS CloudFront configuration

Create a CloudFront distribution: 

In the AWS CloudFront console, create a new web distribution.

Origin domain name: 

Select your S3 bucket as the origin.

Viewer Protocol Policy: 

Set to "Redirect HTTP to HTTPS" for security.

Default root object: 

Set to index.html file.

Cache behaviors: 

Configure caching rules as needed for different file types.

4. Uploading static files with AWS SDK (Boto3)

Use the Python script with Boto3 to upload the contents of your React build directory to your S3 bucket.

Install Boto3 tool.

```

    $ pip install boto3

```

Create Python script to upload static files to S3.

```

    import boto3
    import os

    s3 = boto3.client('s3',
                      aws_access_key_id='YOUR_AWS_ACCESS_KEY_ID',
                      aws_secret_access_key='YOUR_AWS_SECRET_ACCESS_KEY')

    bucket_name = 'your-bucket-name'
    react_build_path = 'path/to/your/react/build'

    for root, dirs, files in os.walk(react_build_path):
        for file in files:
            local_path = os.path.join(root, file)
            s3_path = os.path.relpath(local_path, react_build_path)
            s3.upload_file(local_path, bucket_name, s3_path, ExtraArgs={'ContentType': 'text/html' if file.endswith('.html') else 'application/javascript' if file.endswith('.js') else 'text/css' if file.endswith('.css') else 'image/png' if file.endswith('.png') else 'application/octet-stream'})
            print(f"Uploaded {local_path} to s3://{bucket_name}/{s3_path}")

```

Replace placeholders with your actual AWS credentials and bucket name and adjust ContentType based on file types.
