# Terraform

## The creation, modification, and deletion of GCP resources

By using Infrastructure Manager, you can automate the creation, modification, and deletion of GCP resources like virtual machines, networks, and databases.

Infrastructure Manager automates the process of using Terraform to manage your GCP infrastructure.

A detailed steps on using Infrastructure Manager.

1. Prerequisites

Create a project in the Google Cloud Console and set up billing on that project. 

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

How to set up Terraform and to utilize Terraform in Google's GCP cloud?

To use Terraform with Google Cloud Platform (GCP), you'll need to install Terraform, configure the Google Cloud Provider, and ensure you have appropriate GCP project and service account setup. 

Terraform then uses this configuration to manage your GCP resources as code.

Steps:

1. Install Terraform

Download and install Terraform from the official website.

Verify the installation by running terraform -v in your terminal.

You can install Terraform using package managers like apt (Ubuntu) or yum/dnf (Red Hat/Fedora) or by downloading the Terraform zip file. Then, you'll authenticate with GCP using either the Google Cloud SDK or a service account key, and finally, you'll configure the GCP provider in your Terraform configuration file. 

1.1 Install Terraform

Using package managers (Ubuntu):

Add the HashiCorp GPG key: 

```

$ curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add - 

```

Add the HashiCorp repository: 

```

$ sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main" 

```

Update the package list: 

```

$ sudo apt-get update 

```

Install Terraform: 

```

$ sudo apt-get install terraform 

```

Download and install manually:

Download the latest Terraform zip file for Linux from the official HashiCorp website 

Unzip the file: 

```

$ unzip terraform_VERSION_linux_amd64.zip 

```

Move the terraform executable to a directory in your PATH (e.g., /usr/local/bin): 

```

$ sudo mv terraform /usr/local/bin/ 

```

1.2. Authenticate with GCP

Using the Google Cloud SDK:

Install the Google Cloud SDK (Ubuntu): 

```

$ sudo apt-get install google-cloud-sdk

```

Authenticate: 

```

$ gcloud auth application-default login 

```

Using a service account key:

Create a service account in the Google Cloud Console: navigate to "IAM & Admin" -> "Service accounts" and create a new service account 

Grant the service account necessary roles and permissions 

Generate a key for the service account and download the JSON file 

Set the GOOGLE_APPLICATION_CREDENTIALS environment variable to the path of the JSON key file: export GOOGLE_APPLICATION_CREDENTIALS=path/to/your/key.json 

1.3. Configure the GCP Provider in Terraform

Create a Terraform configuration file (e.g., main.tf) 

Add the provider "google" block to your configuration 

Specify the project, region, and zone 

For authentication using a service account key, you may not need to specify credentials within the provider block if you've set the GOOGLE_APPLICATION_CREDENTIALS environment variable 

Example main.tf file:

```

    provider "google" {
      project = "your-gcp-project-id"
      region  = "your-region"
      zone    = "your-zone"
    }

```

2. Set up GCP

Create a GCP Project: 

In the GCP console, create a new project or select an existing one.

Enable APIs: 

Enable the necessary APIs for the GCP services you intend to use, like Compute Engine, Networking, and Cloud Storage.

Enable Billing: 

Ensure billing is enabled for your GCP project.

3. Authenticate with GCP

Service Account: 

Create a service account in your GCP project.

Service Account Key: 

Generate a JSON key for your service account.

Environment Variable: 

Set the GOOGLE_APPLICATION_CREDENTIALS environment variable to point to the path of the JSON key file. 

Alternatively, you can authenticate using gcloud auth application-default login if you have the Google Cloud CLI installed.

4. Configure the Terraform Google provider

main.tf (or similar): 

In your Terraform configuration files, specify the Google provider plugin. 

This usually involves defining the required_providers block and the provider block.

Project, Region, Zone: In the provider block, define the project, region, and zone where your resources should be created.

5. Write Terraform configuration

Define Resources: 

Write your Terraform configuration files (e.g., main.tf) to define the GCP resources you want to create or manage.

Use Modules: 

Consider using pre-built Terraform modules for common GCP use cases.

6. Initialize Terraform

terraform init: 

Run terraform init to initialize the Terraform configuration directory and download any necessary plugins.

7. Plan and apply

terraform plan: 

Run terraform plan to see the changes that will be made to your infrastructure.

terraform apply: 

Run terraform apply to create the resources in GCP. 

Example:

Here's an example of a main.tf file that creates a Google Cloud Storage bucket: 

```

provider "google" {
  project = "your-project-id"
  region  = "us-central1"
}

resource "google_storage_bucket" "my_bucket" {
  name     = "your-bucket-name"
  location = "us-central1"
}

output "bucket_name" {
  value = google_storage_bucket.my_bucket.name
}

```

### Install Terraform

To install Terraform, visit the official download page and download the appropriate package for your operating system (e.g., Windows, macOS, Linux).

Extract the downloaded file and add the Terraform executable to your system's PATH environment variable.

Here's a more detailed breakdown.

1. Download the Terraform package

Go to the official Terraform download page. 

Select your operating system (Windows, macOS, Linux) and download the corresponding Terraform binary. 

For Windows, you'll typically download a ZIP file containing the executable.

2. Extract and Place the Terraform executable

Unzip the downloaded ZIP file (if applicable). 

Create a new directory for Terraform (e.g., C:\Terraform on Windows). 

Copy the Terraform executable from the extracted folder to the newly created directory. 

3. Add Terraform to your system's PATH:

Windows:

Search for "environment variables" in the Windows search bar and open "Edit the system environment variables". 

Click "Environment Variables..." and then "Path". 

Click "Edit" and add the path to your Terraform directory (e.g., C:\Terraform) to the list of paths. 

Click "OK" to save the changes. 

macOS or Linux:

Open your terminal. 

Add the Terraform directory to your PATH environment variable (e.g., export PATH="$PATH:/path/to/terraform" for Linux/macOS). 

You may need to restart your terminal or open a new one for the changes to take effect. 

4. Verify Installation

Open a new terminal or command prompt.

Type terraform -v (or terraform version) and press Enter.

If Terraform is installed correctly, you should see the installed version number displayed. 

References

Getting Started with the Google Cloud provider

https://registry.terraform.io/providers/hashicorp/google/latest/docs/guides/getting_started