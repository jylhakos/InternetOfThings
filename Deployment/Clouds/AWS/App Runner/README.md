# App Runner

AWS App Runner makes it easier to deploy web applications by taking care of infrastructure management, scaling, and load balancing automatically.

You can either deploy from a container image or source code, and App Runner handles the build and deployment process. 

App Runner provides a secure URL for your application.

Here's how to utilize AWS App Runner for deploying web applications:

1. Choose your source:

Container Image: 

If you have a Docker image of your application, you can push it to Amazon ECR (Elastic Container Registry) and deploy it directly.

Source Code Repository: 

If your application's code is in a GitHub or Bitbucket repository, App Runner can automatically build a container image from it.

2. Create an App Runner service:

Open the App Runner console in the AWS Management Console.

Choose "Create Service".

Select the source type (Container Image or Source Code Repository).

Provide the necessary details for your chosen source (e.g., ECR repository and image tag, or GitHub repository URL and branch).

Configure the runtime, environment variables, and start commands.

Choose a deployment trigger (manual or automatic). 

3. Deploy your application:

If you chose manual deployment, manually initiate the deployment. 

If you chose automatic deployment, changes to your source will trigger deployments.

App Runner will automatically manage infrastructure, scaling, and load balancing.

4. Access your application:

The App Runner service dashboard will provide a URL to access your deployed application.

Verify that the deployment is successful and your application is running.

Additional notes:

Automatic container building:

If you're using a source code repository, App Runner can automatically build a container image based on your application's runtime, build commands, and start commands.

apprunner.yaml:

You can use an apprunner.yaml file in your repository to customize the build process and specify the build and start commands.

VPC Connector:

If your application needs to access resources within your VPC, you can create a VPC connector in App Runner.

AWS CLI or SDKs:

You can also deploy your App Runner services using the AWS CLI or AWS SDKs.

References

Getting started with App Runner

https://docs.aws.amazon.com/apprunner/latest/dg/getting-started.html


![alt text](https://github.com/jylhakos/InternetOfThings/blob/main/JWT/JWT.png?raw=true)
