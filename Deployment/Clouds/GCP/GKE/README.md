# GKE

With GKE, you can configure network, scaling, hardware, and security settings for your containerized apps.

## Deployment of an application to a GKE cluster

1. Build and push the image: 

Cloud Build builds your application, packages it as a Docker image, and pushes it to Container Registry.

2. Create a release in Cloud Deploy

Cloud Build triggers Cloud Deploy, which uses the image from Container Registry to create a new release.

3. Deploy to GKE

Cloud Deploy deploys the release to your GKE cluster. 

References

GKE

https://cloud.google.com/kubernetes-engine/docs/concepts/kubernetes-engine-overview

Deploy an app to a GKE cluster

https://cloud.google.com/kubernetes-engine/docs/deploy-app-cluster

What is Kubeflow?

https://cloud.google.com/discover/what-is-kubeflow
