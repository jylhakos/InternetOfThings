"""
AWS Resources Configuration for Dagster BERT Pipeline
Provides AWS-specific resources for production deployment.
"""

import os
import boto3
from typing import Dict, Any

from dagster import ConfigurableResource, resource
from dagster_aws.s3 import s3_pickle_io_manager, s3_resource
from dagster_aws.ecs import EcsRunLauncher
from dagster_aws.pipes import PipesLambdaClient


class AWSConfig(ConfigurableResource):
    """AWS Configuration settings"""
    region: str = "us-east-1"
    s3_bucket: str = "dagster-bert-pipeline"
    ecs_cluster: str = "dagster-cluster"
    lambda_function_name: str = "bert-inference-lambda"

@resource
def aws_s3_client(context) -> boto3.client:
    """AWS S3 client resource"""
    return boto3.client('s3', region_name=context.resource_config.get("region", "us-east-1"))

@resource
def aws_lambda_client(context) -> boto3.client:
    """AWS Lambda client resource"""
    return boto3.client('lambda', region_name=context.resource_config.get("region", "us-east-1"))

@resource
def aws_ecs_client(context) -> boto3.client:
    """AWS ECS client resource"""
    return boto3.client('ecs', region_name=context.resource_config.get("region", "us-east-1"))

def get_aws_resources() -> Dict[str, Any]:
    """
    Get AWS resources configuration for production deployment.
    """
    aws_region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    s3_bucket = os.getenv("DAGSTER_S3_BUCKET", "dagster-bert-pipeline")
    
    return {
        # I/O Manager for S3 storage
        "io_manager": s3_pickle_io_manager.configured({
            "s3_bucket": s3_bucket,
            "s3_prefix": "dagster/storage"
        }),
        
        # S3 resource
        "s3": s3_resource.configured({
            "region_name": aws_region
        }),
        
        # Amazon AWS clients
        "aws_s3_client": aws_s3_client.configured({
            "region": aws_region
        }),
        
        "aws_lambda_client": aws_lambda_client.configured({
            "region": aws_region
        }),
        
        "aws_ecs_client": aws_ecs_client.configured({
            "region": aws_region
        }),
        
        # Lambda Pipes client for serverless inference
        "lambda_pipes_client": PipesLambdaClient(
            client=boto3.client("lambda", region_name=aws_region)
        ),
        
        # Amazon AWS Configuration
        "aws_config": AWSConfig(
            region=aws_region,
            s3_bucket=s3_bucket
        )
    }

def get_local_resources() -> Dict[str, Any]:
    """
    Get local development resources configuration.
    """
    return {
        "io_manager": s3_pickle_io_manager.configured({
            "s3_bucket": "local-dev-bucket",  # Use LocalStack or MinIO for local S3
            "s3_prefix": "dagster/storage"
        }),
        
        "s3": s3_resource.configured({
            "region_name": "us-east-1"
        })
    }
