# Kubernetes

Kubernetes is a tool for orchestrating and managing containerized applications.

You can define your application's deployment configuration in YAML files, which can be applied to your Kubernetes cluster using kubectl.

## Amazon EKS

Amazon EKS (Elastic Kubernetes Service) operates Kubernetes on AWS by managing the control plane, whereas users are responsible for managing the worker nodes.

Kubernetes service

Amazon EKS is a managed Kubernetes service, meaning AWS handles the complexities of the control plane (API server, etcd, etc.).

Worker nodes

Users are responsible for managing the worker nodes, which are the EC2 instances that run your containers.

Integration with AWS:

Amazon EKS integrates seamlessly with other AWS services like VPC, IAM, and load balancers.

## GCP GKE

Google Kubernetes Engine (GKE) makes it easier to deploy Docker containers by offering a managed Kubernetes service within Google Cloud.

GKE cluster has a control plane and machines called nodes. 

Nodes run the services supporting the containers that make up your workload. 

The control plane decides what runs on those nodes, including scheduling and scaling. 

## Azure AKS

Azure Kubernetes Service (AKS) offers the deployment and management of Docker containers on Kubernetes.

AKS handles the underlying Kubernetes infrastructure, automating tasks like upgrades, scaling, and monitoring.

References

Learn Kubernetes Basics

https://kubernetes.io/docs/tutorials/kubernetes-basics/

Kubernetes concepts

https://docs.aws.amazon.com/eks/latest/userguide/kubernetes-concepts.html

Containerize an application

https://docs.docker.com/get-started/workshop/02_our_app/

Deploy to Kubernetes

https://docs.docker.com/guides/kube-deploy/

Amazon Elastic Kubernetes Service

https://docs.aws.amazon.com/eks/

Google Kubernetes Engine (GKE)

https://cloud.google.com/kubernetes-engine

Building a Machine Learning platform with Kubeflow and Ray on Google Kubernetes Engine

https://cloud.google.com/blog/products/ai-machine-learning/build-a-ml-platform-with-kubeflow-and-ray-on-gke

What is Azure Kubernetes Service (AKS)?

https://learn.microsoft.com/en-us/azure/aks/what-is-aks
