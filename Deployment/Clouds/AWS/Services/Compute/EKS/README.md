# Kubernetes

Amazon EKS (Elastic Kubernetes Service) is a Kubernetes-as-a-Service (KaaS) solution that delivers a managed environment for operating Kubernetes clusters, while users manage the worker nodes and utilize options like Fargate for serverless node management.

![alt text](https://github.com/jylhakos/InternetOfThings/blob/main/Deployment/Clouds/AWS/Services/Compute/EKS/Amazon_EKS.png?raw=true)

*Figure: Amazon Elastic Kubernetes Service (EKS)*

Setting up tools to configure AWS EKS on a local Linux machine.

1. AWS CLI installation and configuration

Install the AWS CLI: 

Follow the instructions on the AWS documentation page for your Linux distribution (e.g., using apt or yum or downloading the zip file and installing).

Download the AWS CLI installer:

Use curl to download the appropriate zip file for your system (e.g., curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip").

Unzip the installer:

Use the unzip command to extract the contents of the zip file (e.g., unzip awscliv2.zip).

Run the install script:

Navigate to the extracted directory and run the install script (e.g., sudo ./aws/install).

Configure the AWS CLI: 

Use the aws configure command to set up your AWS credentials (access key, secret key, region, and output format).

2. kubectl installation

Download the latest kubectl binary for your Linux distribution.

To set up and configure kubectl using the apt package manager on Debian:

```

    $ sudo apt-get update && sudo apt-get install -y apt-transport-https ca-certificates curl

    $ curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo gpg --dearmor -o /etc/apt/keyrings/
    kubernetes-archive-keyring.gpg
    
    $ echo "deb [signed-by=/etc/apt/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list

    $ sudo apt-get update

    $ sudo apt-get install -y kubectl

```
Configure AWS credentials using aws configure command.

```

	$ aws configure

```
You will be prompted to enter the access key, secret key, region, and output format.

Run aws configure and enter your AWS Access Key ID, Secret Access Key, default region, and output format.

If your environment supports IAM roles, configure your instance to assume the appropriate role.

Create environment variables to assume the IAM role.

Set the AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and AWS_REGION environment variables before running kubectl tool.

```

	$ export AWS_ACCESS_KEY_ID=RoleAccessKeyID

	$ export AWS_SECRET_ACCESS_KEY=RoleSecretKey

	$ export AWS_SESSION_TOKEN=RoleSessionToken

```

Find the ARN of the IAM role you want to assume. 

```

    $ aws iam list-roles --query "Roles[?RoleName == 'your-role-name'].[RoleName, Arn]"

```
Replace your-role-name with the actual role name. 

Use the aws sts assume-role command to assume the IAM role.

```

	$ aws sts assume-role --role-arn "your-role-arn" --role-session-name "your-session-name"

```

To use an assumed IAM role with kubectl to interact with an EKS cluster, you need to first assume the role using the AWS CLI and then configure your kubectl to use the assumed role's credentials.

Configure kubeconfig for EKS

If you need to grant the assumed role access to the EKS cluster, you might need to add the role to the aws-auth ConfigMap in your cluster. 

This allows the role to authenticate with the EKS cluster.

```

    $ kubectl edit configmap aws-auth -n kube-system

```

Add a new entry under mapRoles with the role ARN and appropriate Kubernetes roles/groups.

```

    mapRoles: |
      - rolearn: arn:aws:iam::123456789012:role/your-role-name
        username: system:node:{{EC2PrivateDNSName}}
        groups:
          - system:bootstrappers
          - system:nodes

```
Using aws eks update-kubeconfig command.

Use the following command to create or update the kubeconfig file, replacing placeholders with your cluster details:

```

    $ aws eks update-kubeconfig --region <your-aws-region> --name <your-cluster-name>

```
Run kubectl version --client to verify the kubectl version and kubectl get svc to test the connection to your cluster.

3. eksctl installation

Download the latest eksctl binary for your Linux distribution.

Make the eksctl binary executable and move it to a directory in your system's PATH.

Example: Debian commands using curl to install AWS CLI, kubectl and eksctl tools:

```

	# Install AWS CLI (example using curl)
	curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
	unzip awscliv2.zip
	sudo ./aws/install

	# Configure AWS CLI
	aws configure

	# Install kubectl
	curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
	sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

	# Install eksctl
	ARCH=amd64
	PLATFORM=$(uname -s | tr '[:upper:]' '[:lower:]')
	curl -fsSL "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$PLATFORM_$ARCH.tar.gz" | tar xz -C /tmp
	sudo mv /tmp/eksctl /usr/local/bin

	# Verify installation
	aws --version
	kubectl version --client
	eksctl version

```
After setting up the Kubernetes tools, you can create an EKS cluster using eksctl command.

```

	$ eksctl create cluster --name my-eks-cluster --region your-aws-region --nodeg钙roup-name my-ng --nodes 2 --nodes-min 1 --nodes-max 3

```
The example eksctl command creates an EKS cluster named my-eks-cluster in the specified AWS region, with a node group named my-ng containing 2 nodes initially (with a minimum of 1 and a maximum of 3).

## Example: Deploying Go application with Docker container to run on Kubernetes

1. Prerequisites

First, ensure you have Docker, Docker Compose (optional for local development), AWS CLI v2, eksctl and kubectl tools installed.

Next create a Go web application for example the following code.

The main.go file

```

	package main

	import (
	    "fmt"
	    "log"
	    "net/http"
	    "os"
	)

	func main() {
	    port := os.Getenv("PORT")
	    if port == "" {
	        port = "8080"
	    }

	    http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
	        fmt.Fprintf(w, "A Go application running on Kubernetes.")
	    })

	    http.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
	        w.WriteHeader(http.StatusOK)
	        fmt.Fprintf(w, "OK")
	    })

	    log.Printf("Server starting on port %s", port)
	    log.Fatal(http.ListenAndServe(":"+port, nil))
	}

```

The mod.go file

```

	module go-k8s-app

	go 1.21

```

2. Dockerizing a Go web application

Dockerizing a Go web application involves creating a Dockerfile that defines the environment and steps required to build and run your application within a Docker container.

A Dockerfile for a Go application uses a multi-stage build for efficiency and smaller image sizes.

Create Dockerfile

```

	# Stage 1: Build the Go web application
	FROM golang:1.21-alpine AS builder

	WORKDIR /app
	COPY go.* ./
	RUN go mod download

	COPY . .
	RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main .

	# Stage 2: Create the minimal image for a production
	FROM alpine:latest

	RUN apk --no-cache add ca-certificates
	WORKDIR /root/

	COPY --from=builder /app/main .

	EXPOSE 8080

	CMD ["./main"]

```

Explanation of Dockerfile commands:

FROM golang:latest AS builder

Uses the official Go image as the base for the build stage. AS builder names this stage.

WORKDIR /app

Sets the working directory inside the container.

COPY go.mod go.sum ./ and RUN go mod download

Copies the module files and downloads dependencies to leverage Docker's layer caching.

COPY . . 

Copies the entire application source code into the container.

RUN CGO_ENABLED=0 GOOS=linux go build -o main .

Builds the Go application into a binary named main. CGO_ENABLED=0 disables CGO for static linking, and GOOS=linux targets Linux.

FROM alpine:latest

Uses a lightweight Alpine Linux image for the final stage, reducing image size.

COPY --from=builder /app/main .

Copies only the compiled binary from the builder stage to the final image.

EXPOSE 8080

Informs Docker that the container listens on port 8080.

CMD ["./main"]

Specifies the command to execute when the container starts, running your compiled Go application.

3. Create Docker Compose for local development

```

	version: '3.8'

	services:
	  go-app:
	    build: .
	    ports:
	      - "8080:8080"
	    environment:
	      - PORT=8080
	    restart: unless-stopped
	    healthcheck:
	      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:8080/health"]
	      interval: 30s
	      timeout: 10s
	      retries: 3

```

4. Build and push Docker image

```

	#!/bin/bash

	# Set variables
	AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
	# Change to your preferred region
	AWS_REGION="us-west-2"  
	IMAGE_NAME="go-k8s-app"
	IMAGE_TAG="latest"

	# Create ECR repository if it doesn't exist
	aws ecr describe-repositories --repository-names $IMAGE_NAME --region $AWS_REGION || \
	aws ecr create-repository --repository-name $IMAGE_NAME --region $AWS_REGION

	# Get login token and login to ECR
	aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

	# Build Docker image
	docker build -t $IMAGE_NAME:$IMAGE_TAG .

	# Tag for ECR
	docker tag $IMAGE_NAME:$IMAGE_TAG $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$IMAGE_NAME:$IMAGE_TAG

	# Push to ECR
	docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$IMAGE_NAME:$IMAGE_TAG

	echo "Image pushed to: $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$IMAGE_NAME:$IMAGE_TAG"

```

5. Create EKS cluster

The cluster-config.yaml file:

```

	apiVersion: eksctl.io/v1alpha5
	kind: ClusterConfig

	metadata:
	  name: go-app-cluster
	  region: us-west-2
	  version: "1.28"

	nodeGroups:
	  - name: go-app-workers
	    instanceType: t3.medium
	    desiredCapacity: 2
	    minSize: 1
	    maxSize: 4
	    volumeSize: 20
	    ssh:
	      allow: true
	    iam:
	      withAddonPolicies:
	        imageBuilder: true
	        autoScaler: true
	        certManager: true
	        efs: true
	        ebs: true
	        fsx: true
	        cloudWatch: true

	addons:
	  - name: vpc-cni
	  - name: coredns
	  - name: kube-proxy
	  - name: aws-ebs-csi-driver

	cloudWatch:
	  clusterLogging:
	    enable: ["audit", "authenticator", "controllerManager"]

```

Create the EKS cluster using eksctl:

```

	#!/bin/bash

	# Create EKS cluster
	eksctl create cluster -f cluster-config.yaml

	# Update kubeconfig
	aws eks update-kubeconfig --region us-west-2 --name go-app-cluster

	# Verify cluster connection
	kubectl get nodes

```

6. Create Kubernetes deployment.yaml deployment manifests file

```

	apiVersion: apps/v1
	kind: Deployment
	metadata:
	  name: go-app-deployment
	  labels:
	    app: go-app
	spec:
	  replicas: 3
	  selector:
	    matchLabels:
	      app: go-app
	  template:
	    metadata:
	      labels:
	        app: go-app
	    spec:
	      containers:
	      - name: go-app
	        image: YOUR_AWS_ACCOUNT_ID.dkr.ecr.us-west-2.amazonaws.com/go-k8s-app:latest
	        ports:
	        - containerPort: 8080
	        env:
	        - name: PORT
	          value: "8080"
	        resources:
	          requests:
	            memory: "64Mi"
	            cpu: "250m"
	          limits:
	            memory: "128Mi"
	            cpu: "500m"
	        livenessProbe:
	          httpGet:
	            path: /health
	            port: 8080
	          initialDelaySeconds: 30
	          periodSeconds: 10
	        readinessProbe:
	          httpGet:
	            path: /health
	            port: 8080
	          initialDelaySeconds: 5
	          periodSeconds: 5
	---
	apiVersion: v1
	kind: Service
	metadata:
	  name: go-app-service
	spec:
	  selector:
	    app: go-app
	  ports:
	    - protocol: TCP
	      port: 80
	      targetPort: 8080
	  type: ClusterIP


```

7. Create Ingress configuration (ALB) ingress.yaml file

```

	apiVersion: networking.k8s.io/v1
	kind: Ingress
	metadata:
	  name: go-app-ingress
	  annotations:
	    kubernetes.io/ingress.class: alb
	    alb.ingress.kubernetes.io/scheme: internet-facing
	    alb.ingress.kubernetes.io/target-type: ip
	    alb.ingress.kubernetes.io/healthcheck-path: /health
	spec:
	  rules:
	  - http:
	      paths:
	      - path: /
	        pathType: Prefix
	        backend:
	          service:
	            name: go-app-service
	            port:
	              number: 80

```

8. Install AWS Load Balancer (ALB) controller

Helm is the package manager for the Kubernetes services.

Download the Helm binary release for your system.

Use curl to download the Helm binary release for Linux.

```

    $ curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3


```

Change permissions to make Helm executable, and then move it to a directory in your PATH.

```

	$ chmod 700 get_helm.sh
	    
	$ ./get_helm.sh

```

Create the install-alb-controller.sh file to install the AWS Load Balancer controller using Helm.

```

	#!/bin/bash

	# Create IAM OIDC provider
	eksctl utils associate-iam-oidc-provider --region=us-west-2 --cluster=go-app-cluster --approve

	# Create IAM role for AWS Load Balancer controller
	eksctl create iamserviceaccount \
	  --cluster=go-app-cluster \
	  --namespace=kube-system \
	  --name=aws-load-balancer-controller \
	  --role-name AmazonEKSLoadBalancerControllerRole \
	  --attach-policy-arn=arn:aws:iam::aws:policy/ElasticLoadBalancingFullAccess \
	  --approve

	# Install AWS Load Balancer controller
	kubectl apply -k "github.com/aws/eks-charts/stable/aws-load-balancer-controller//crds?ref=master"

	helm repo add eks https://aws.github.io/eks-charts
	helm repo update

	helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
	  -n kube-system \
	  --set clusterName=go-app-cluster \
	  --set serviceAccount.create=false \
	  --set serviceAccount.name=aws-load-balancer-controller

```
9. Deploy Go web application to Kubernetes

```

	#!/bin/bash

	# Apply Kubernetes manifests
	kubectl apply -f deployment.yaml
	kubectl apply -f ingress.yaml

	# Check deployment status
	kubectl get deployments
	kubectl get pods
	kubectl get services
	kubectl get ingress

	# Get ALB URL
	echo "Application will be available at:"
	kubectl get ingress go-app-ingress -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'

```
### References

What is Amazon EKS?

https://docs.aws.amazon.com/eks/latest/userguide/what-is-eks.html

Learn Kubernetes Basics

https://kubernetes.io/docs/tutorials/kubernetes-basics/

Kubernetes concepts

https://docs.aws.amazon.com/eks/latest/userguide/kubernetes-concepts.html

Amazon Elastic Kubernetes Service Documentation

https://docs.aws.amazon.com/eks/

Set up to use Amazon EKS

https://docs.aws.amazon.com/eks/latest/userguide/setting-up.html

Installing or updating to the latest version of the AWS CLI

https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html

Set up kubectl and eksctl

https://docs.aws.amazon.com/eks/latest/userguide/install-kubectl.html

Deploy a sample application on Linux

https://docs.aws.amazon.com/eks/latest/userguide/sample-deployment.html

Deploy a web app and store data

https://docs.aws.amazon.com/eks/latest/userguide/quickstart.html


Helm

https://helm.sh/docs/

Deploy applications with Helm on Amazon EKS

https://docs.aws.amazon.com/eks/latest/userguide/helm.html

View Kubernetes resources in the AWS Management Console

https://docs.aws.amazon.com/eks/latest/userguide/view-kubernetes-resources.html

Practical exercises to learn about Amazon Elastic Kubernetes Service

https://www.eksworkshop.com/
