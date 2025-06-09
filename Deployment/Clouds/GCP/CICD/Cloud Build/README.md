# Cloud Build

To set up Cloud Build for application builds on Google Cloud Platform (GCP), you need to enable the Cloud Build API, grant it the necessary permissions, and configure your project with a build configuration file. Cloud Build then executes the build, and if applicable, artifacts are pushed to Artifact Registry. 

## Utilizing Cloud Build

1. Enable Cloud Build API

Navigate to the Cloud Build API page in the GCP console.

Enable the API.

2. Set Permissions

Ensure the Cloud Build service account has the required permissions.

This is crucial for Cloud Build to interact with other GCP services.

3. Create a Build Configuration File

Create a cloudbuild.yaml or cloudbuild.json file.

This file contains instructions for Cloud Build, including build steps, source code location, and target deployment.

An example cloudbuild.yaml file

```

    steps:
    - name: 'gcr.io/cloud-builders/maven'
      args: ['mvn', 'clean', 'install']
    images:
    - 'gcr.io/$PROJECT_ID/my-app:latest'

```

4. Submit the Build

Use the gcloud builds submit command.

This initiates the build process using the Cloud Build service.

5. View Build details

Open the Cloud Build page in the GCP console.

View the build history, including the status, logs, and artifacts. 

### Deploying to Cloud Run

Enable Cloud Run APIs: 

Enable the Cloud Run functions API.

Grant permissions: 

Grant the Cloud Run functions Developer role to the Cloud Build service account.

Configure Cloud Build: 

Update your cloudbuild.yaml file to include steps for deploying to Cloud Run.

### Building and pushing Docker images:

Configure Build: Specify the Dockerfile location and build context in your cloudbuild.yaml.

Push to Artifact Registry: Add a step to push the built image to Artifact Registry.

### Automating Builds with Triggers:

Create a Trigger: 

Configure a trigger to automatically start builds when changes are pushed to a source code repository. 

Connect Repository: 

Connect your repository (e.g., GitHub, Bitbucket) to Cloud Build. 

Configure Trigger: 

Specify the branch or tags that should trigger a build. 

References

Cloud Build

https://cloud.google.com/build/docs/overview


Setting up Cloud Build

https://cloud.google.com/build/docs/set-up


