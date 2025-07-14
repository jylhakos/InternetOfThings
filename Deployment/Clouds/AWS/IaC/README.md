# Infrastructure as Code (IaC)

What is Infrastructure as Code?

Infrastructure as code (IaC) refers to the capability of provisioning and managing your computing infrastructure through code rather than relying on manual processes and configurations.

An application requires various infrastructure components, including operating systems, database connections, and storage. 

In the past, DevOps teams depended on scripts and manual processes to set up infrastructure environments.

You can now automate the configuration of your environment through Infrastructure as Code (IaC), enabling a more efficient and automated process.

AWS offers the following services to define infrastructure as code.

- AWS CloudFormation

- AWS Serverless Application Model (AWS SAM)

- AWS Cloud Development Kit (AWS CDK)

- AWS Cloud Development Kit for Kubernetes

- AWS Cloud Development Kit for Terraform

- AWS Cloud Control API

To utilize IaC for deploying web applications on AWS, you can leverage tools like AWS CloudFormation or Terraform, defining your infrastructure needs in templates or configuration files, which are then used to provision and manage your AWS resources.

Key Steps:

1. Define an infrastructure:

Clearly outline the resources required for your web application, including EC2 instances, load balancers, databases, storage, and networking components.

2. Choose an IaC tool:

Select either AWS CloudFormation (AWS's native IaC service) or Terraform (a popular third-party tool).

3. Create IaC templates or configurations:

Write IaC templates or configurations (using JSON or YAML for CloudFormation, or Terraform's HCL language) that describe your desired infrastructure state. 

4. Version Control:

Store your IaC templates or configurations in a version control system (like Git) to track changes and enable collaboration.

5. Deploy and Manage:

Use the chosen IaC tool to deploy your infrastructure, and then use the IaC tool to manage any changes or updates to the deployed infrastructure.

IaC tools:

AWS CloudFormation:

AWS's native service for defining and managing AWS infrastructure as code. You can create templates in JSON or YAML to provision resources like EC2 instances, load balancers, VPCs, and more.

Terraform:

A third-party tool that allows you to define your infrastructure using declarative configuration files (in HCL). Terraform can manage various cloud providers, including AWS, and offers a range of features, including modules for reusability and state management.

AWS CDK (Cloud Development Kit):

A code-first approach to IaC, allowing you to define your AWS infrastructure using programming languages like Python or TypeScript. The CDK generates CloudFormation templates for deployment. 

An example to utilize Terraform to deploy a web application:

Let's say you want to deploy a web application consisting of an EC2 instance, a load balancer, and an RDS database. 

Using Terraform, you could define these resources in separate modules (or separate sections within the same file) and then deploy them using a Terraform plan and apply process. 

You would define your desired state, including the EC2 instance type, AMI, and security group rules, the load balancer configuration, and the database parameters. 

### References

Reviewing IaC tools for the AWS Cloud

https://docs.aws.amazon.com/prescriptive-guidance/latest/choose-iac-tool/iac-tools.html

Choosing an IaC tool

https://docs.aws.amazon.com/prescriptive-guidance/latest/choose-iac-tool/choose-tool.html

AWS CloudFormation

https://docs.aws.amazon.com/whitepapers/latest/introduction-devops-aws/aws-cloudformation.html

AWS Serverless Application Model (AWS SAM)

https://docs.aws.amazon.com/whitepapers/latest/introduction-devops-aws/aws-serverless-application-model.html

AWS Cloud Development Kit (AWS CDK)

https://docs.aws.amazon.com/whitepapers/latest/introduction-devops-aws/aws-cdk.html

AWS Cloud Development Kit for Kubernetes

https://docs.aws.amazon.com/whitepapers/latest/introduction-devops-aws/aws-cdk-for-kubernetes.html

AWS Cloud Development Kit for Terraform

https://docs.aws.amazon.com/whitepapers/latest/introduction-devops-aws/aws-cdk-for-terraform.html

AWS Cloud Control API

https://docs.aws.amazon.com/whitepapers/latest/introduction-devops-aws/aws-cloud-control-api.html

![alt text](https://github.com/jylhakos/InternetOfThings/blob/main/JWT/JWT.png?raw=true)
