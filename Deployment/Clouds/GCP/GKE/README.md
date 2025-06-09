# GKE

## Deploying to GKE

1. Build and push the image: 

Cloud Build builds your application, packages it as a Docker image, and pushes it to Container Registry.

2. Create a release in Cloud Deploy

Cloud Build triggers Cloud Deploy, which uses the image from Container Registry to create a new release.

3. Deploy to GKE

Cloud Deploy deploys the release to your GKE cluster. 

References

