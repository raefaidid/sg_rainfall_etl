from airflow import DAG
from airflow.providers.google.cloud.operators.gcs import GCSCreateBucketOperator
from datetime import datetime

# Default arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
}

# Define the DAG
with DAG(
    dag_id='create_gcs_bucket',
    default_args=default_args,
    description='A simple DAG to create a GCS bucket',
    schedule_interval=None,  # Run on demand
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['gcs', 'example'],
) as dag:
    
    # Task to create a GCS bucket
    create_bucket = GCSCreateBucketOperator(
        task_id='create_bucket',
        bucket_name='airflow-test-002',  # Replace with your desired bucket name
        location='asia-southeast1',  # Specify the GCS bucket location
        storage_class = "REGIONAL",
        project_id='love-bonito-iv',  # Replace with your GCP project ID
        gcp_conn_id="airflow-conn-id"
    )

create_bucket