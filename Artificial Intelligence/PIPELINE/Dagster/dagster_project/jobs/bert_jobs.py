"""
Dagster Jobs for BERT Pipeline
Defines the complete pipeline workflow.
"""

from dagster import define_asset_job, AssetSelection

# Define the complete BERT pipeline job
bert_pipeline_job = define_asset_job(
    name="bert_pipeline_job",
    description="Complete BERT fine-tuning, evaluation, and deployment pipeline",
    selection=AssetSelection.all(),
    tags={
        "dagster/max_runtime": "3600",  # 1 hour timeout
        "owner": "ml-team",
        "pipeline": "bert-training"
    }
)

# Define individual pipeline stages as separate jobs
data_preparation_job = define_asset_job(
    name="data_preparation_job",
    description="Prepare training dataset for BERT fine-tuning",
    selection=AssetSelection.groups("data_preparation"),
    tags={
        "stage": "data-prep",
        "owner": "data-team"
    }
)

training_job = define_asset_job(
    name="training_job",
    description="Fine-tune BERT model",
    selection=AssetSelection.groups("model_training"),
    tags={
        "stage": "training",
        "owner": "ml-team",
        "dagster/max_runtime": "7200"  # 2 hours for training
    }
)

evaluation_job = define_asset_job(
    name="evaluation_job",
    description="Evaluate trained BERT model",
    selection=AssetSelection.groups("model_evaluation"),
    tags={
        "stage": "evaluation",
        "owner": "ml-team"
    }
)

deployment_job = define_asset_job(
    name="deployment_job",
    description="Deploy BERT model for inference",
    selection=AssetSelection.groups("model_deployment", "model_testing"),
    tags={
        "stage": "deployment",
        "owner": "ops-team"
    }
)
