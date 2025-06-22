# React application run on Docker Container

Deploying a React application with Docker involves containerizing the application and its dependencies into a single unit.

Create a Dockerfile: 

This file defines the instructions for building your Docker image. 

For a React application, a common approach is to use a multi-stage build:

Build stage:

Use a Node.js base image to install dependencies and build the React application (e.g., npm run build).

Serve stage:

Use a lightweight web server image, such as Nginx or Apache, to serve the static build files generated in the previous stage.

## Example: Dockerfile for React application run on Nginx

If you are using Nginx, create an nginx.conf file in the same directory as your Dockerfile to configure how Nginx serves your React application.

Dockerfile

```

    # Build stage
    FROM node:lts-alpine as build
    WORKDIR /app
    COPY package*.json ./
    RUN npm ci
    COPY . .
    RUN npm run build

    # Serve stage
    FROM nginx:latest as production
    COPY --from=build /app/build /usr/share/nginx/html
    COPY nginx.conf /etc/nginx/nginx.conf
    EXPOSE 80
    CMD ["nginx", "-g", "daemon off;"]

```

The nginx.conf file


```

    events {}
    http {
        include /etc/nginx/mime.types;
        server {
            listen 80;
            server_name localhost;
            root /usr/share/nginx/html;
            index index.html index.htm;
            location / {
                try_files $uri $uri/ /index.html;
            }
        }
    }

```

Build the Docker image.

```

    $ docker build -t your-react-app-name .

```

Run the Docker container.

```

    $ docker run -p 80:80 your-react-app-name

```
Deployment (optional): 

For production, you would push your Docker image to a container registry (e.g., Docker Hub, Amazon ECR, Azure Container Registry) and then deploy it to a cloud platform or a server running Docker.
