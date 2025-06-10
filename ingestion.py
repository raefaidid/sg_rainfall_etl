import pandas as pd
import requests
import json
from airflow import DAG
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

 
def call_api(**context):
    url = "https://api-open.data.gov.sg/v2/real-time/api/rainfall"
    response = requests.get(url)
    dct_data = response.json()
    context["ti"].xcom_push(key="raw_data", value=response.json())

    
def create_stations_tbl(**context):
    """
    Unnest and store api data into Pandas Dataframe
    """
    
    api_data = context["ti"].xcom_pull(key="raw_data") 
    
    stations = api_data['data']['stations']
    
    stations_schema = {
        "columns" : ["station_id", "device_id", "station_name", "station_latitude", "station_longitude"],
        "datatype" : "string"
    }
    
    lst_stations = []
    
    for station in stations:
        temp_dct_stations = {}
        temp_dct_stations["station_id"] = station["id"]
        temp_dct_stations["device_id"] = station["deviceId"]
        temp_dct_stations["station_name"] = station["name"]
        temp_dct_stations["station_latitude"] = station["location"]["latitude"]
        temp_dct_stations["station_longitude"] = station["location"]["longitude"]
        lst_stations.append(temp_dct_stations)
    
    stations_ppdf = pd.DataFrame(data = lst_stations, columns = stations_schema["columns"], dtype = stations_schema["datatype"])
    
    context["ti"].xcom_push(key="stations_data", value=stations_ppdf.to_json())


def create_readings_tbl(**context):
    """
    Unnest and store api data into Pandas Dataframe
    """
    
    api_data = context["ti"].xcom_pull(key="raw_data") 
    
    readings = api_data['data']['readings']
    
    readings_schema = {
        "columns" : ["station_id", "rainfall_reading", "timestamp"],
        "datatype" : "string"
    }
    
    lst_readings = []
    
    for reading in readings:
        for data in reading['data']:
            temp_dct_readings = {}
            temp_dct_readings["timestamp"] = reading["timestamp"]
            temp_dct_readings["station_id"] = data["stationId"]
            temp_dct_readings["rainfall_reading"] = data["value"]
            lst_readings.append(temp_dct_readings)
    
    readings_ppdf = pd.DataFrame(data = lst_readings, columns = readings_schema["columns"], dtype = readings_schema["datatype"])
    
    context["ti"].xcom_push(key="readings_data", value=readings_ppdf.to_json())
    

def create_rainfall_dataset(**context):
    
    stations = pd.read_json(context["ti"].xcom_pull(key="stations_data"))
    readings = pd.read_json(context["ti"].xcom_pull(key="readings_data"))
    
    rainfall_ppdf = readings.merge(stations, on="station_id", how="left")
    rainfall_ppdf = rainfall_ppdf[["timestamp", "rainfall_reading", "station_id", "station_name","station_latitude",
                                   "station_longitude", "device_id"]]
    
    context["ti"].xcom_push(key="unnested_data", value=rainfall_ppdf.to_json())


def export_csv_locally(**context):
    rainfall_ppdf = pd.read_json(context["ti"].xcom_pull(key="unnested_data"))
    local_filepath = f'/home/raef_aidid/airflow/data/sg_rainfall.csv'
    rainfall_ppdf.to_csv(local_filepath, index=False)



default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}



# Define the DAG
with DAG(
    dag_id='ingestion_sg_rainfall_data',
    default_args=default_args,
    description='Ingestion of raw data from API',
    schedule_interval= "*/5 * * * *",  # Run on demand
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['gcs', 'love-bonito'],
) as dag:
    
    call_api_task = PythonOperator(
        task_id="call_api_sg_rainfall", python_callable=call_api
    )
    
    create_stations_tbl_task = PythonOperator(
        task_id="create_stations_tbl", python_callable=create_stations_tbl
    )
    
    create_readings_tbl_task = PythonOperator(
        task_id="create_readings_tbl", python_callable=create_readings_tbl
    )
    
    create_rainfall_dataset_task = PythonOperator(
        task_id="create_rainfall_dataset", python_callable=create_rainfall_dataset
    )
    
    export_csv_locally_task = PythonOperator(
        task_id="export_csv_locally", python_callable=export_csv_locally
    )
    
    dump_file_to_gcs = LocalFilesystemToGCSOperator(
        task_id="upload_file",
        src='/home/raef_aidid/airflow/data/sg_rainfall.csv',  # Local path of the file
        dst=f'raw/sg_rainfall_' + datetime.today().strftime('%Y-%m-%d %H:%M:%S' + '.csv'),  # Destination path in GCS (including the object name)
        bucket='sg_rainfall',  # GCS bucket name
    )
    
    call_api_task >> [create_stations_tbl_task, create_readings_tbl_task] >> create_rainfall_dataset_task >> export_csv_locally_task >> dump_file_to_gcs
    
    