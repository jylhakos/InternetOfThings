# Example: Java with Spring Boot application that provides static files for a React component utilizing AWS CloudFront.

To write Java with Spring Boot application that serves static files using AWS Content Delivery Network (CDN) — specifically Amazon CloudFront — together with local server (such as Nginx) distribution, you’ll want to:

1. Host your static assets (e.g., images, JS, CSS) on Amazon S3.

Place your static files (images, JS, CSS, etc.) in an S3 bucket.

Make sure the bucket has the right permissions for CloudFront to access.

2. Configure an Amazon CloudFront distribution to serve content from S3 (the CDN part).

Set the S3 bucket as the origin of your CloudFront distribution.

Configure cache behaviors as needed.

Note the CloudFront domain name, e.g. d1234.cloudfront.net.

3. Configure your web app (React) to load assets (e.g., logo.png) from the CloudFront URL.

React app loads static assets from CloudFront URLs.

For example, edit your image tag in React.

```

	<img src="https://d1234.cloudfront.net/logo.png" alt="Logo" />

```
Or, if you use environment variables in React.

Set REACT_APP_CDN_URL=https://d1234.cloudfront.net in your .env file.

```

	<img src={`${process.env.REACT_APP_CDN_URL}/logo.png`} alt="Logo" />

```

4. Let your Spring Boot backend serve dynamic content (APIs, etc.), but not static files.

By default, Spring Boot serves static resources from /static or /public directories. To prevent this (and avoid serving static files from your backend), you can either remove static files from these folders or configure Spring Boot to route static file paths elsewhere directories.

5. Optionally, configure Nginx to reverse-proxy API requests to Spring Boot and static file requests to CloudFront.

Nginx proxies API calls to Spring Boot, static file calls to CloudFront.

Proxy /api/* or other backend requests to your Spring Boot app.

Proxy /static/*, /assets/*, or other static requests directly to CloudFront.

An example Nginx config file

```

	server {
	    listen 80;
	    server_name example.com;

	    location /api/ {
	    	# Spring Boot server
	        proxy_pass http://localhost:8080; 
	        proxy_set_header Host $host;
	        proxy_set_header X-Real-IP $remote_addr;
	    }

	    location /static/ {
	        proxy_pass https://d1234.cloudfront.net/static/;
	    }

	    location / {
	    	# Your built React app
	        root /usr/share/nginx/html; 
	        try_files $uri $uri/ /index.html;
	    }
	}

```
References

Get started with CloudFront

https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/GettingStarted.html

Static Content

https://docs.spring.io/spring-boot/reference/web/servlet.html#web.servlet.spring-mvc.static-content