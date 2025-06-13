# Google Cloud Platform (GCP)

Google's public cloud service provides a range of solutions, including virtual machines, containerized applications, and serverless computing.

## Sign up Google Cloud Platform

To sign up for a Google Cloud Platform (GCP) account and get the $300 free trial, you can follow these steps: 

1. Navigate to the Google Cloud Page:

Go to the official Google Cloud Free Program page. 

You can find it by searching for "Google Cloud Free Program" or by visiting the link: cloud.google.com/free. 

2. Click "Get Started for Free" or "Start Free":

Look for the button that initiates the free trial sign-up process. 

It might be labeled "Get Started for Free" or "Start Free".

3. Sign in with your Google Account:

You will be prompted to sign in with your Google Account (Gmail ID). If you don't have one, create a new one first.

4. Fill in Account Details and Payment Information:

You'll need to provide details like your country, name, and address. 

You'll also need to provide a credit card or other payment method for identity verification purposes. 

Why Google Cloud Platform?

Google Cloud Platform users can take advantage of a 90-day trial period that includes 300 dollars in free Cloud Billing credits.

Free Tier provides limited access to many common Google Cloud services:

- App Engine

- Artifact Registry

- BigQuery

- Cloud Build

- Cloud Deploy

- Compute Engine

- Google Kubernetes Engine

- Cloud Run

- Cloud Shell

- Cloud Storage

- Workflows

## Examples of GCP services

App Engine: 

A platform for developing, building and hosting web applications.

App Engine offers a managed environment and simplifies deployment with commands like gcloud app deploy.

Cloud Run: 

Creates containers without virtual machines.

For Cloud Run, you can use the gcloud run deploy command to deploy from source code, and GCP will handle the Docker build. 

Compute Engine:

Provides virtual machines.

For Compute Engine, you can SSH into the VM and deploy your application as you would on any computer.

Create a VM:

https://accounts.google.com/
      
In the Google Cloud Console, navigate to Compute Engine and create a new VM instance.

Choose an image and size:

Select a Linux image (e.g., Ubuntu) and choose an appropriate machine type based on your application's needs.

Configure networking:

Set up the VM's network, including a public IP address. 

You may need to create a firewall rule to allow HTTP/HTTPS traffic.

SSH into the VM: 

Connect to the VM using SSH through the console. 

Deploy the application: 

Follow deployment procedures (e.g., using web servers like Apache, Nginx, or deploying a Docker container).
      
Copy your web application files (HTML, CSS, JavaScript, etc.) to the web server's document root (e.g., /var/www/html).

Google Kubernetes Engine (GKE): 

A managed Kubernetes service.

BigQuery: 

A serverless, enterprise-level data warehouse.

## Utilizing GCP cloud for deploying and managing applications.

You can utilize different services on Google Cloud Platform (GCP) for deploying and managing applications based on your specific application type and requirements.

You can deploy to services like App Engine (for web apps), Cloud Run (for containers), or Google Kubernetes Engine (GKE) for more complex containerized deployments. 

The Google Cloud console and the Google Cloud SDK (gcloud) are key tools for deploying and managing applications. 

1. App Engine

Deployment:

Use the gcloud app deploy command to deploy your application to App Engine, which will upload your code and configure the application environment. 

This command builds your application into a container image and deploys it to either the Standard or Flexible environments.

Management:

App Engine offers features for scaling, versioning, and monitoring your applications. 

You can manage your application through the Google Cloud console.

Use Cases:

Suitable for web applications, APIs, and other applications that require a managed environment. 

2. Cloud Run

Deployment:

Create a Dockerfile to package your web application into a container image.

Deploy your application using a container image.

Build and deploy:

Use the gcloud run deploy command to deploy your container from source code, or from a specified container image.

You can either use the Cloud Run console or the gcloud CLI to deploy.

Cloud Run automatically handles building and deploying the image if a Dockerfile is present.

Management:

Cloud Run automatically scales your application based on demand. 

You can also manage traffic routing, versioning, and other aspects of your application.

Use Cases:

Ideal for serverless applications, microservices, and APIs that require high scalability and automation. 

3. Google Kubernetes Engine (GKE)

Deployment:

Deploy your application by creating Kubernetes deployments, services, and other resources. 

You can use the gcloud CLI or the Kubernetes control plane to manage your cluster.

Create a GKE cluster:

In the Google Cloud Console, navigate to Kubernetes Engine and create a new cluster.

Package your application: 

Containerize your application using Docker.

Create Kubernetes manifests:

Define how your application should be deployed within the cluster, including deployments, services, and ingress.

Use kubectl apply to deploy your application to the GKE cluster.

Configure a Kubernetes service to expose your application to external traffic.

Management:

GKE provides tools for scaling, versioning, and managing your Kubernetes cluster and deployments.

Use Cases:

Suitable for containerized applications that require more control over the underlying infrastructure and Kubernetes features. 

4. Other GCP Services

Cloud Build:

Use Cloud Build to automatically build and package your application into container images. 

Artifact Registry:

Store your container images in Artifact Registry for easy access and management. 

Cloud Deploy:

Use Cloud Deploy for CI/CD and automated releases to GKE or Cloud Run. 

Cloud Monitoring & Cloud Logging:

Use these services to monitor your applications and log events for troubleshooting. 

5. Deployment procedures

Create a Google Cloud Project: Set up a project in the Google Cloud console to manage your resources. 

Install gcloud CLI: Install the Google Cloud SDK (gcloud) for command-line interaction with GCP. 

Authenticate: Authenticate with your Google Cloud account using gcloud auth login. 

Configure Project: Set the default project for gcloud using gcloud config set project <your_project_id>. 

Choose a Service: Select the appropriate service for your application type (App Engine, Cloud Run, GKE). 

Deploy: Use the appropriate command for your chosen service (e.g., gcloud app deploy, gcloud run deploy). 

Manage: Use the Google Cloud console and gcloud CLI to manage your application, including scaling, versioning, and monitoring.

### Set up a provider in Google's GCP cloud.

To set up a provider in Google’s GCP cloud, you typically need to authenticate with GCP and provide the necessary provider details along with configuration parameters.

Configuring the provider typically requires creating a service account, defining project and region or zone details, and possibly utilizing a configuration file or Terraform provider.

Here’s an overview of the process.

1. Authentication

```

	$ gcloud auth application-default login

```

The gcloud command authenticates using your default application credentials, which is a good starting point for development.

Service Account: 

For production environments, using a service account is recommended for better security and control. 

This involves creating a service account in GCP, generating a key, and using it for authentication.

Setting up a service account in GCP

To create a service account in the Google Cloud Platform (GCP) console, navigate to the Service Accounts page, select a project, and then click the "Create Service Account" button.

IAM roles:

Ensure your service account has the necessary IAM roles to create and manage the resources you intend to deploy.

Terraform: 

If using Terraform, you'll need to specify your credentials within the provider configuration. 

2. Provider details and configuration

Project: Specify the Google Cloud project ID where your resources will be created.

Region and Zone: Determine the geographical location (region) and specific zone within that region where resources will be deployed.

Configuration File (if applicable): Some tools, like Terraform, use configuration files to define the infrastructure. 

You'll specify the provider and its attributes within this file.

A sample of Terraform usage.

```

	provider "google" {
          project = "your-project-id"
          region  = "us-central1"
          # Optional:  Specify credentials if not using default authentication
          # credentials = <<EOF
          # {
          #   "type": "service_account",
          #   "project_id": "your-project-id",
          #   "private_key": "<<your-private-key>>",
          #   "client_email": "<<your-client-email>>",
          #   "client_id": "<<your-client-id>>"
          # }
          # EOF
          # }
        }

```

## Set up your Google Cloud project


To create a Google Cloud project, navigate to the Google Cloud Console, select "IAM & Admin," then "Create a Project." 

Provide a project name, ID, and choose a billing account. 

1. Sign in and navigate: 

Sign in to your Google Cloud account and navigate to the Google Cloud Console.

2. Create a project: 

Go to Menu > IAM & Admin > Create a Project.

3. Enter project details

Project Name: 

Give your project a descriptive name.

Project ID: 

This is a unique identifier for your project. 

Choose an ID that you'll be comfortable using for the lifetime of the project.

Billing Account: 

Select the billing account you want to use for the project. If you don't have one, you can create one later.

4. Choose a location: 

Select a location for your project resources. You can browse available locations.

5. Select organization: 

If you want to link your project to an organization, you can select it here.

6. Create: Click the "Create" button to finalize the project creation.

After creating the project, you can install the Google Cloud CLI for managing it. 

To deploy an application to App Engine, first create or select a Google Cloud project. 

Next, enable billing for the project, which is required for deployment. 

Then, configure App Engine within the project by selecting a region, service account, and enabling billing. 

Finally, use the gcloud app deploy command to deploy your application.

Detailed Steps:

1. Select or create a Google Cloud Project

You can either choose an existing project or create a new one in the Google Cloud Console.

2. Enable Billing

Ensure billing is enabled for the project. 

If you don't have a billing account, you'll need to create one and associate it with your project.

3. Configure App Engine

Select a Region: 

Choose a region for your App Engine application's deployment.

Select a Service Account: Choose or create a service account with the necessary permissions.

4. Deploy your application

Use the gcloud app deploy command to upload your application to App Engine. 

This command will automatically build your application into a container image and deploy it to the App Engine environment.

5. Configure Deployment

If using Cloud Code for IntelliJ, select the server configuration (Google App Engine) and specify the project.

Choose a deployment source, such as a Maven or Gradle artifact.

Fill in other deployment fields as needed.

6. Monitor Deployment:

Use the Application Servers window in Cloud Code to monitor the deployment progress.

### An example to deploy a web application

What are the steps to deploy a web application from a local computer to Google Cloud Platform (GCP)?

To deploy a web application from a computer to GCP, you can use various services depending on your application type and deployment needs.

You can deploy to Compute Engine (VM instances), Cloud Run (containerized apps), or App Engine (managed application environment).


![alt text](https://github.com/jylhakos/InternetOfThings/blob/main/JWT/JWT.png?raw=true)

References

Free to sign up

https://cloud.google.com/free?hl=en

Free Tier 

https://cloud.google.com/free/docs/free-cloud-features


Google Cloud Setup

https://cloud.google.com/docs/enterprise/cloud-setup

Set up your Google Cloud project

https://developers.google.com/maps/documentation/android-sdk/cloud-setup


Deploy your application

https://cloud.google.com/deploy/docs/deploying-application

Deploy your web service

https://cloud.google.com/appengine/docs/standard/nodejs/building-app/deploying-web-service

Google Cloud CLI

https://cloud.google.com/sdk/docs/install

Go Cloud Development Kit (Go CDK)

https://github.com/google/go-cloud

Create GCP service accounts

https://cloud.google.com/iam/docs/service-accounts-create

Terraform Provider for Google Cloud Platform

https://github.com/hashicorp/terraform-provider-google

Overview of Terraform on Google Cloud

https://cloud.google.com/docs/terraform/terraform-overview
