# LOVE, BONITO - Data Engineer Technical Assessment: Singapore Rainfall ETL
This repository presents the solution for the Data Engineer Technical Assessment provided by LOVE, BONITO, focusing on the ETL (Extract, Transform, Load) process for Singapore rainfall data. 


## Project Overview
The core objective of this assessment is to design and implement a data pipeline to extract, process, and present rainfall data from the data.gov.sg API, along with an alert mechanism for significant rainfall events. 

## Current Progress: Data Extraction
Due to current time constraints and the inherent complexity of setting up a self-hosted orchestration tool like Apache Airflow on a Virtual Machine, I have focused on delivering a robust solution for the data extraction component.  This ensures a fundamental capability is in place, demonstrating the ability to acquire the raw data necessary for subsequent stages.

I have prepared a deck as an overview for the pipeline: [Singapore Rainfall ETL](https://docs.google.com/presentation/d/1d3swsyjuENiiHelahvuG70Re2n2AqJvHH7GVd87CxDI/edit?slide=id.g3659eb20e97_0_15#slide=id.g3659eb20e97_0_15) 

## Implemented Solution
The current solution reliably fetches data from the provided API endpoint:
https://data.gov.sg/datasets/d_6580738cdd7db79374ed3152159fbd69/view#tag/default/GET/rainfall

- Extraction Logic: A Python script (ingestion.py) has been developed to connect to the API, retrieve the rainfall data, and handle initial parsing.
- Technology Used: Python.
- Manual Upload: For this submission, the extracted data are stored inside Google Cloud Storage and the extraction script are manually uploaded to this GitHub repository while app files such as Airflow are residing inside the VM. This serves as a tangible output of the extraction phase.

You may try to view the extracted data here: [GCS Bucket](https://console.cloud.google.com/storage/browser/sg_rainfall/raw?inv=1&invt=Abzu_g&project=love-bonito-iv&pageState=(%22StorageObjectListTable%22:(%22f%22:%22%255B%255D%22)))

<img width="1149" alt="Screenshot 2025-06-11 at 7 18 31 AM" src="https://github.com/user-attachments/assets/d7f1f8f8-4c52-4b65-bfe9-a07e5ec857c5" />

<img width="1408" alt="Screenshot 2025-06-11 at 7 19 58 AM" src="https://github.com/user-attachments/assets/dd3190c6-fe15-4d2c-b7ad-de1d3b737946" />

## Comprehensive Solution Design (Ideation: Physical Design)
My design for the full-scale production solution leverages Google Cloud Platform (GCP) to create a scalable, robust, and automated ETL pipeline.  This design addresses all requirements of the technical assessment, from data ingestion to reporting and alerting.

## Proposed Architecture & Technologies 
The envisioned architecture for the complete ETL pipeline is as follows:

- Data Source: data.gov.sg API 
- Orchestration: Apache Airflow, deployed on Google Compute Engine, for scheduling and managing the ETL workflows. 
- Raw Data Storage: Ingest raw data directly into Google Cloud Storage for cost-effective and scalable object storage. This acts as a data lake for immutable raw data. 
- Data Transformation & Warehousing: Transformed data will be loaded into Google BigQuery, a serverless, highly scalable, and cost-effective cloud data warehouse, ideal for analytical queries. 
BigQuery's robust SQL capabilities will be used to process and transform the raw data to answer queries such as:
1. Top 10 areas of highest rainfall.
2. Top 10 areas of lowest rainfall population.
3. Hourly rainfall distribution across Singapore.
- Reporting & Dashboarding: Data from BigQuery will feed into Looker Studio (formerly Google Data Studio) to create interactive dashboards for the data team. This dashboard will visualize rainfall distribution and allow for querying the specified metrics.
- Alert Mechanism: Logic to identify areas exceeding average rainfall will be implemented as part of the Airflow pipeline or a separate service (e.g., Cloud Functions). Alerts will be sent via Gmail to the data team, ensuring timely notification. 

## Folder Structure (Conceptual)
The planned folder structure within Google Cloud Storage (GCS) buckets would follow a medallion architecture or similar, categorizing data by its processing stage:
1. raw/: For original, untransformed data.
2. transformed/: For cleaned, structured, and aggregated data ready for analysis.
3. business/: For highly refined datasets optimized for specific business reporting or AI model training. 
