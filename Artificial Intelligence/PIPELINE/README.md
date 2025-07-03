# AI pipeline


## Example: AI pipeline on AWS by Ray or MLflow

Ray and MLflow can be used to build AI/ML pipelines on AWS

Ray on AWS

Ray is an open-source framework designed for scaling AI and Python workloads on AWS, with integrations to various AWS services.

Ray can be used throughout the ML workflow, including data analysis, feature engineering, and model training, utilizing services like Amazon EC2, Amazon EMR, and Amazon SageMaker.

Deployment options include self-managed clusters on Amazon EC2 or Amazon EKS, and integration with SageMaker's managed infrastructure. 

Resources like the aws-do-ray project can assist with deployment on Amazon EKS or SageMaker Hyperpod.

Key integrations include data storage with Amazon S3 and distributed file systems, training and tuning with SageMaker, model serving with Ray Serve, and security/monitoring using AWS IAM, ACM, KMS, and CloudWatch.

MLflow on AWS

MLflow is an open-source platform for managing the ML lifecycle, covering experiment tracking, model management, and deployment.

Amazon SageMaker provides a fully managed MLflow capability for easier setup and management of Tracking Servers.

Using MLflow with SageMaker simplifies experiment tracking across different environments, unifies model governance by automatically registering models in the SageMaker Model Registry, simplifies deployment to SageMaker Inference, and provides secure access via AWS IAM roles. 

SageMaker's managed infrastructure reduces overhead and enhances security with AWS PrivateLink support.


Ray and MLflow on AWS

Ray Core can be integrated with MLflow using child runs within Ray tasks.


References

Amazon SageMaker

https://aws.amazon.com/sagemaker/

Scaling AI and Machine Learning Workloads with Ray on AWS

https://aws.amazon.com/blogs/opensource/scaling-ai-and-machine-learning-workloads-with-ray-on-aws/

LLM experimentation at scale using Amazon SageMaker Pipelines and MLflow

https://aws.amazon.com/blogs/machine-learning/llm-experimentation-at-scale-using-amazon-sagemaker-pipelines-and-mlflow/
