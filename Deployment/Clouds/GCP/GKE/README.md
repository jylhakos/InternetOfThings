# Google Kubernetes Engine (GKE)

With GKE, you can configure network, scaling, hardware, and security settings for your containerized apps.

To connect to a Google Kubernetes Engine (GKE) cluster using kubectl, you need to install the Google Cloud CLI (gcloud) and kubectl, configure gcloud with your Google account, and then retrieve the cluster's credentials.

1. Install Google Cloud SDK (gcloud) and kubectl

Install gcloud:

Follow the instructions on the [Google Cloud documentation](https://cloud.google.com/sdk/docs/install) to download and install the Google Cloud SDK for Debian.

Install kubectl:

You can either install kubectl as part of the Google Cloud SDK using gcloud components install kubectl or install it separately using your Debian's package manager.

2. Configure gcloud

Authenticate:

Run gcloud auth login to authenticate with your Google Cloud account. This will open a browser window for you to log in.

Set project and zone:

Use gcloud config set project PROJECT_ID and gcloud config set compute/zone ZONE to set your project ID and the zone or region where your GKE cluster is located. Replace PROJECT_ID and ZONE with your actual values.

3. Configure kubectl

Retrieve cluster credentials:

Execute gcloud container clusters get-credentials CLUSTER_NAME --zone ZONE --project PROJECT_ID to fetch the necessary credentials for your cluster.

Replace CLUSTER_NAME, ZONE, and PROJECT_ID with your cluster's name, zone, and project ID.

If you are connecting to a private cluster, you might need to configure your network to allow access to the cluster's control plane. 

The gcloud container clusters get-credentials command automatically updates your ~/.kube/config file with the information.

## Example: Deployment of a web application with Docker to a GKE cluster

1. Prerequisites

Install the tools

```

	# Install Google Cloud SDK
	$ curl https://sdk.cloud.google.com | bash

	$exec -l $SHELL

	# Install kubectl by gcloud
	$ gcloud components install kubectl

	# Or install kubectl by curl
	$ curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"

	$ chmod +x kubectl

	$ sudo mv kubectl /usr/local/bin/

```

Configure gcloud

```

	# Authenticate with Google Cloud
	gcloud auth login

	# Set your project
	gcloud config set project YOUR_PROJECT_ID

	# Set default compute zone
	gcloud config set compute/zone us-central1-a

```

2. Create GKE cluster

```

	# Create a GKE cluster
	$ gcloud container clusters create my-go-app-cluster \
	    --num-nodes=3 \
	    --enable-autoscaling \
	    --min-nodes=1 \
	    --max-nodes=5 \
	    --zone=us-central1-a

	# Get credentials for kubectl
	$ gcloud container clusters get-credentials my-go-app-cluster --zone=us-central1-a

```

3. Create a web application

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
	        fmt.Fprintf(w, "Go app running on GKE.")
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

	module go-gke-app

	go 1.21

```

4. Dockerize the web application

Create Dockerfile for the web application

```

	FROM golang:1.21-alpine AS builder

	WORKDIR /app
	COPY go.mod go.sum ./
	RUN go mod download

	COPY . .
	RUN CGO_ENABLED=0 GOOS=linux go build -o main .

	FROM alpine:latest
	RUN apk --no-cache add ca-certificates
	WORKDIR /root/

	COPY --from=builder /app/main .

	EXPOSE 8080
	CMD ["./main"]

```

Build and push Docker image

```

	# Configure Docker to use gcloud as credential helper
	$ gcloud auth configure-docker

	# Build the Docker image
	$ docker build -t gcr.io/YOUR_PROJECT_ID/go-web-app:latest .

	# Push to Google Container Registry
	$ docker push gcr.io/YOUR_PROJECT_ID/go-web-app:latest

```
Cloud Build builds your application, packages it as a Docker image, and pushes it to Container Registry.

Docker Compose alternative (for local development)

```
	version: '3.8'
	services:
	  go-web-app:
	    build: .
	    ports:
	      - "8080:8080"
	    environment:
	      - PORT=8080
	    restart: unless-stopped
	    healthcheck:
	      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
	      interval: 30s
	      timeout: 10s
	      retries: 3

```

5. Create a release in Cloud Deploy (Optional)

Cloud Build triggers Cloud Deploy, which uses the image from Container Registry to create a new release.

6. Configure Kubernetes

The deployment.yaml file

```

	apiVersion: apps/v1
	kind: Deployment
	metadata:
	  name: go-web-app
	  labels:
	    app: go-web-app
	spec:
	  replicas: 3
	  selector:
	    matchLabels:
	      app: go-web-app
	  template:
	    metadata:
	      labels:
	        app: go-web-app
	    spec:
	      containers:
	      - name: go-web-app
	        image: gcr.io/YOUR_PROJECT_ID/go-web-app:latest
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

```

The service.yaml file

```

	apiVersion: v1
	kind: Service
	metadata:
	  name: go-web-app-service
	spec:
	  selector:
	    app: go-web-app
	  ports:
	    - protocol: TCP
	      port: 80
	      targetPort: 8080
	  type: LoadBalancer

```

The ingress.yaml configuration (Optional)

```

	apiVersion: networking.k8s.io/v1
	kind: Ingress
	metadata:
	  name: go-web-app-ingress
	  annotations:
	    kubernetes.io/ingress.class: "gce"
	    kubernetes.io/ingress.global-static-ip-name: "go-web-app-ip"
	spec:
	  rules:
	  - host: your-domain.com
	    http:
	      paths:
	      - path: /
	        pathType: Prefix
	        backend:
	          service:
	            name: go-web-app-service
	            port:
	              number: 80

```

Use ConfigMaps and Secrets for configuration.

The configmap.yaml file

```

	apiVersion: v1
	kind: ConfigMap
	metadata:
	  name: go-web-app-config
	data:
	  app.properties: |
	    environment=production
	    log.level=info

```
7. Deploy the web application to GKE

Cloud Deploy deploys the release to your GKE cluster (Optional).

Use kubctl command to deploy the web application to GKE.

```

	# Apply Kubernetes configurations
	$ kubectl apply -f deployment.yaml
	$ kubectl apply -f service.yaml
	$ kubectl apply -f configmap.yaml  # if using
	$ kubectl apply -f ingress.yaml    # if using

	# Check deployment status
	$ kubectl get deployments
	$ kubectl get pods
	$ kubectl get services

	# Get external IP (for LoadBalancer service)
	$ kubectl get service go-web-app-service

	# View logs
	$ kubectl logs -l app=go-web-app

	# Scale deployment
	$ kubectl scale deployment go-web-app --replicas=5

``` 

References

GKE

https://cloud.google.com/kubernetes-engine/docs/concepts/kubernetes-engine-overview

Deploy an app to a GKE cluster

https://cloud.google.com/kubernetes-engine/docs/deploy-app-cluster

Install the gcloud CLI

https://cloud.google.com/sdk/docs/install

Set up Kubernetes tools

https://kubernetes.io/docs/tasks/tools/

Install kubectl and configure cluster access

https://cloud.google.com/kubernetes-engine/docs/how-to/cluster-access-for-kubectl

What is Kubeflow?

https://cloud.google.com/discover/what-is-kubeflow
