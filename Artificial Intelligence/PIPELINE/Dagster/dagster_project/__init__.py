"""
Dagster BERT Fine-tuning Pipeline
Main entry point for the Dagster project containing all definitions.
"""

import os
from dagster import Definitions, load_assets_from_modules
from dagster_aws.s3 import s3_pickle_io_manager, s3_resource

from dagster_project.assets import bert_assets
from dagster_project.resources.aws_resources import get_aws_resources
from dagster_project.jobs.bert_jobs import bert_pipeline_job
from dagster_project.schedules.bert_schedules import bert_training_schedule

# Environment detection
IS_LOCAL_DEV = os.getenv("DAGSTER_IS_DEV_CLI") == "1"
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

# Load all assets
bert_assets_list = load_assets_from_modules([bert_assets])

# Configure resources based on environment
if IS_LOCAL_DEV:
    # Local development resources
    resources = {
        "io_manager": s3_pickle_io_manager,
        "s3": s3_resource,
    }
else:
    # Production AWS resources
    resources = get_aws_resources()

# Main Dagster definitions
defs = Definitions(
    assets=bert_assets_list,
    jobs=[bert_pipeline_job],
    schedules=[bert_training_schedule] if not IS_LOCAL_DEV else [],
    resources=resources,
)
