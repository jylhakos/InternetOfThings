# Infrastructure Manager

By using Infrastructure Manager, you can automate the creation, modification, and deletion of GCP resources like virtual machines, networks, and databases.

Infrastructure Manager automates the process of using Terraform to manage your GCP infrastructure.

## A detailed steps on using Infrastructure Manager.

Infrastructure Manager automates the process of using Terraform to manage your GCP infrastructure.

Below is a detailed steps on using Infrastructure Manager.

1. Prerequisites

Enable the Infrastructure Manager API:

In your Google Cloud console, navigate to the API Library, search for "Infrastructure Manager", and enable the API.

Install Terraform

Ensure you have a supported version of Terraform installed locally. 

Create or Select a Project:

Create a new Google Cloud project or select an existing one where you want to deploy your infrastructure. 

Set up Authentication:

You'll need a service account with the config.agent role to allow Infrastructure Manager to interact with your Google Cloud resources.

2. Defining Your Infrastructure (Terraform)

Write your Terraform configuration:

Use Terraform to define the infrastructure resources you need for your application. This might include creating virtual machines, networks, load balancers, and other GCP resources.

Store your Terraform code:

You can store your Terraform configuration in a Git repository or in a Cloud Storage bucket.

3. Deploying with Infrastructure Manager

Choose a Deployment Source: 

Select either your Git repository or Cloud Storage bucket as the source for your Terraform configuration.

Specify the Deployment ID: 

Give your deployment a descriptive name.

Select a Region: 

Choose a supported region where your infrastructure will be deployed.

Choose a Terraform Version: 

Select a supported Terraform version that's compatible with your code and the region.

Configure the Service Account: 

Select the service account you created with the config.agent role.

4. Managing your Infrastructure

Infrastructure Manager uses Terraform: Infra Manager acts as a tool to initiate and manage Terraform deployments.

Cloud Build: 

It creates a Cloud Build job to execute Terraform's init, validate, plan, and apply stages, automatically managing the process.

Monitoring and Logging: 

Infra Manager streams Cloud Build logs to a Cloud Storage bucket, providing visibility into the deployment process. 


References

Infrastructure Manager overview 

https://cloud.google.com/infrastructure-manager/docs/overview

Deploy infrastructure using Infrastructure Manager

https://cloud.google.com/infrastructure-manager/docs/deploy-resources

Deploy a VPC with Terraform

https://cloud.google.com/infrastructure-manager/docs/deploy-vpc-with-terraform

