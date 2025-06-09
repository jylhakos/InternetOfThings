# Containers

To deploy an application using containers, you typically build a container image, then run that image as a container on a host machine or in a cloud environment. 

## Deploy an application using containers

1. Build a Container Image

Use a Dockerfile (or similar) to define the container's configuration, including the base image, application code, dependencies, and instructions for installing them.

Build the image using a container engine like Docker.

2. Run the Container

Use a container engine to create and run a container from the built image.

The container will execute the application code within its isolated environment.

3. Manage Containers

Use container orchestration platforms like Kubernetes to manage, deploy, and scale multiple containers.

Kubernetes can handle tasks like load balancing, automatic scaling, and rolling updates. 

## Docker

Deploying applications with Docker involves several key steps: building a Docker image from a Dockerfile, pushing the image to a registry, pulling the image to the target machine, and running the container. 

You can use tools like Docker Compose for multi-container deployments or orchestrators like Kubernetes for managing and scaling containerized applications. 

Steps:

1. Create a Dockerfile

This file contains instructions for building the Docker image, including defining the base image, copying files, installing dependencies, and setting environment variables.

Dockerfile example

```

    FROM ubuntu:latest
    RUN apt-get update -y && apt-get install -y nginx
    COPY ./index.html /usr/share/nginx/html/
    EXPOSE 80
    CMD ["nginx", "-g", "daemon off;"]

```

2. Build the Docker Image

Use the docker build command to create a Docker image based on the Dockerfile.

```

$ docker build -t <my-app> .

```

3. Push the Docker Image to a Registry

Share your image with others by pushing it to a public or private registry like Docker Hub or your own internal registry.

4. Pull the Docker Image

On the target machine, use the docker pull command to download the image from the registry.

5. Run the Docker Container

Use the docker run command to create and start a container from the image.

```

$ docker run -d -p 8080:80 my-web-app

```

6. Access the Application

Make sure the container's ports are mapped to your host's ports so you can access the application from your browser or other clients.

Open your web browser and go to http://localhost:8080

### Docker Compose

For multi-container applications, create a docker-compose.yml file to define the services, networks, and volumes.
Use the docker-compose up command to start all the services.


## Kubernetes

Kubernetes is a powerful tool for orchestrating and managing containerized applications.

You can define your application's deployment configuration in YAML files, which can be applied to your Kubernetes cluster using kubectl.

References

Containerize an application

https://docs.docker.com/get-started/workshop/02_our_app/

Deploy to Kubernetes

https://docs.docker.com/guides/kube-deploy/

