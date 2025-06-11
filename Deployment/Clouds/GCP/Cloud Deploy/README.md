# Cloud Deploy

Cloud Deploy automates the deployment process, integrating with tools like Cloud Build and Kubernetes.

To use Cloud Deploy, you'll define a delivery pipeline with multiple stages and targets, then create releases to move your application through the pipeline.

## The details to follow step-by-step.

1. Prerequisites

Enabled a Google Cloud project and billing. 

Install the Google Cloud CLI (or use Cloud Shell).

Enable required APIs (Cloud Deploy, Cloud Build, Cloud Run, Cloud Storage, etc.).

2. Define your delivery pipeline

Create a Delivery Pipeline: 

In the Cloud Console, navigate to Cloud Deploy and create a delivery pipeline.

Specify Pipeline Name, Region, and Runtime: 

Choose a name, select a region (e.g., us-central1), and the runtime (GKE or Cloud Run).

Define Targets: 

Targets represent deployment locations (e.g., GKE clusters, Cloud Run services). 

For each target, specify:

Target Name: 

A unique name for the target.

Runtime: (GKE or Cloud Run).

Cluster or region: 

If GKE, select the cluster; if Cloud Run, select the region.

Optionally, configure rollout approval: 

You can require approval before promoting a release to a target.

3. Create a release

Initiate a release: 

Create a release to start the deployment process.

Specify release details: 

Provide a release name and optionally, a version.

Automatic rollout: 

Cloud Deploy automatically creates a rollout for the first target in the pipeline.

4. Promote the release

Promote to Subsequent Targets: Once the first rollout is complete, you can promote the release to the next target(s) in the pipeline.

Automatic Rollout: 

Each promotion creates a new rollout for the specified target. 

### Using the CLI for Cloud Run

1. Create a delivery pipeline

Defines the sequence of deployment targets and how the application will be deployed. 

```

   $ gcloud deploy pipelines create your-pipeline-name \
     --region=us-central1 \
     --description="My Cloud Deploy pipeline"

```

2. Create a target (Cloud Run)

Represent the deployment environments where your application will run. 

```

   $ gcloud deploy targets create run \
     --name=your-target-name \
     --region=us-central1 \
     --service=your-service-name \
     --project=your-project-id

```

3. Create a release


Represent a specific version of your application that is deployed and the deployment process to a specific target. 

```

	$ gcloud deploy releases create your-release-name \
     --delivery-pipeline=your-pipeline-name \
     --region=us-central1

```

4. Promote the release

```

	$ gcloud deploy rollouts create --promote \
     --release=your-release-name \
     --delivery-pipeline=your-pipeline-name \
     --region=us-central1

```

References

Cloud Deploy

https://cloud.google.com/deploy/docs/overview

