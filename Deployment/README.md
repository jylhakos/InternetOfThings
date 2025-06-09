# Evaluate the cloud services offered by Amazon AWS, Microsoft Azure, and Google GCP

The table outlines Google's GCP services alongside their equivalent offerings in Amazon Web Services (AWS) and Microsoft Azure.

| _Service Type_     | _Service Description_                                 | **GCP**                | **AWS**                   | **Azure**            |
|--------------------|-------------------------------------------------------|------------------------|---------------------------|----------------------|
| API management     | Design, secure, analyze  and scale APIs               | Apigee                 | Amazon Publisher          | Azure API Management |
| API security       | Help to protect your APIs  From security threats      | Advanced               |                           | Defender             |
| Cost Optimization  | Optimize cloud usage with  actionable recommendations | Recommender            | AWS Cost Optimization     | Cost Management      |
| Compute            | Block storage For VM instances                        | Google Cloud Hyperdisk | Elastic Block Store (EBS) | Managed Disks        |
| Deployment         | Configure and deploy                                  | Workload Manager       | Launch Wizard             | Center for SAP       |
| Container services | CI/CD                                                 | Cloud Deploy           | CodeDeploy                | DevOps               |

## Deploying and managing applications across AWS, Azure and GCP

Terraform uses cloud providers to manage resources in different clouds.

Terraform modules could be used to create the following:

Networking Module: Defines the VPCs, subnets, and security groups for each cloud.

Compute Module: Provisions EC2 instances, VMs, or other compute resources based on the chosen cloud provider.

Storage Module: Creates S3 buckets, Azure Blob Storage, or Google Cloud Storage buckets to store web assets or application data.

You define configurations for each cloud provider, then use Terraform modules to encapsulate reusable infrastructure components like networking and compute resources.

1. Setting up provider configuration:

AWS:

You'll need to configure the AWS provider, specifying your AWS access key, secret key, and region.

Azure:

Similarly, configure the Azure provider, including your Azure subscription ID, client ID, client secret, and tenant ID.

GCP:

For GCP, you'll need to set up the GCP provider, using your GCP project ID, credentials file (e.g., service account key), and region.


2. Defining modules for reusable infrastructure:

Create Terraform modules for common infrastructure components, such as VPCs, networking, storage, and compute resources.

Each module will contain the Terraform code specific to a particular cloud provider (AWS, Azure, or GCP).

Use variables within the modules to make them flexible and reusable across different environments.

3. Deploying to cloud providers:

AWS:

Use modules to provision resources like EC2 instances, S3 buckets, IAM roles, and VPCs within AWS.

Azure:

Deploy Azure resources like virtual machines, resource groups, storage accounts, and virtual networks using appropriate Terraform modules.

GCP:

Utilize Terraform modules to create Google Cloud resources like VMs, storage buckets, VPCs, and service accounts.

4. Managing state files:

For managing infrastructure state across multiple cloud providers, consider using a remote backend, such as an S3 bucket or Azure Storage Account, to store state files.

5. Orchestrating deployments:

Use a CI/CD pipeline to automate the deployment process, triggering Terraform deployments when code changes are made.

Employ tools like Jenkins, CircleCI, or GitLab CI to manage and orchestrate these deployments.

References

Compare AWS and Azure services to Google Cloud

https://cloud.google.com/docs/get-started/aws-azure-gcp-service-comparison

Markdown tables

https://www.tablesgenerator.com/markdown_tables

References


![alt text](https://github.com/jylhakos/InternetOfThings/blob/main/JWT/JWT.png?raw=true)
