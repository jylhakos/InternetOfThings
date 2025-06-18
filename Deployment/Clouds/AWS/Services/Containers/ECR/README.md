# Elastic Container Registry (ECR)

To deploy a Docker image from your local linux machine to AWS ECR (Elastic Container Registry), you'll first need to authenticate Docker to your AWS account, then create an ECR repository, tag your Docker image with the ECR repository URI, and finally, push the image to the repository.

Here’s an outline of the steps involved.

1. Prerequisites

AWS CLI: 

Ensure you have the AWS CLI installed and configured with your AWS credentials.

Docker: 

Make sure Docker is installed and running on your Linux machine.

IAM user: 

Have an IAM user with permissions to interact with ECR (e.g., AmazonEC2ContainerRegistryFullAccess policy).

2. Authenticate Docker to AWS ECR:

Use the aws ecr get-login-password command to retrieve an authentication token.

Pipe the output to docker login to authenticate your Docker client with the ECR registry. 

```

    $ aws ecr get-login-password --region <your_region> | docker login --username AWS --password-stdin <your_aws_account_id>.dkr.ecr.<your_region>.amazonaws.com

```

Replace <your_region> and <your_aws_account_id> with your AWS region and account ID, respectively. 

3. Create an ECR Repository (if it doesn't exist)

Use the AWS CLI to create a repository:

```

    $ aws ecr create-repository --repository-name <your_repository_name> --region <your_region>

```

Replace <your_repository_name> with your desired repository name.

Alternatively, you can create a repository in the AWS Management Console.

4. Tag your Docker image

Identify the local image you want to push using docker images.

Tag your image with the ECR repository URI:

```

    $ docker tag <your_image_name>:<your_tag> <your_aws_account_id>.dkr.ecr.<your_region>.amazonaws.com/<your_repository_name>:<your_tag>

```

Replace <your_image_name>, <your_tag>, and other placeholders with your actual values. 

Check:

You can verify the image is pushed by checking the ECR repository in the AWS Management Console or by listing images using the AWS CLI.
