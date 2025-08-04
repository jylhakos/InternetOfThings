"""
Dagster Schedules for BERT Pipeline
Defines automated scheduling for the pipeline.
"""

from dagster import schedule, ScheduleEvaluationContext
from dagster_project.jobs.bert_jobs import bert_pipeline_job, training_job

@schedule(
    cron_schedule="0 2 * * 1",  # Every Monday at 2 AM
    job=bert_pipeline_job,
    execution_timezone="UTC"
)
def bert_training_schedule(context: ScheduleEvaluationContext):
    """
    Weekly schedule for complete BERT pipeline execution.
    Runs every Monday at 2 AM UTC.
    """
    return {
        "tags": {
            "scheduled_run": "true",
            "schedule_name": "weekly_bert_training"
        }
    }

@schedule(
    cron_schedule="0 6 * * *",  # Daily at 6 AM
    job=training_job,
    execution_timezone="UTC"
)
def bert_daily_training_schedule(context: ScheduleEvaluationContext):
    """
    Daily schedule for BERT model training only.
    Useful for continuous model improvement.
    """
    return {
        "tags": {
            "scheduled_run": "true",
            "schedule_name": "daily_bert_training"
        }
    }
