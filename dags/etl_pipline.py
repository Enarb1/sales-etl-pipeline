from airflow.sdk import dag, task
from pendulum import datetime

from include.etl.extract.extract_raw_data_s3 import extract_paths
from include.config.settings import AWS_CONN_ID, BUCKET_NAME, RAW_DATA_FOLDER, PROCESSED_DATA_FOLDER
from include.etl.transform.clean import clean_dfs
from include.etl.transform.merge import sales_product_merge, enrich_merged_sales_product
from include.etl.transform.aggregations import hourly_sales_trend, sales_product_trend, seasonal_sales_pattern, \
    revenue_concentration


@dag(
    dag_id='etl_pipline',
    schedule='@daily',
    start_date=datetime(2026, 7, 1),
    catchup=True,
)
def etl_pipline():
    @task
    def extract_raw_data(aws_conn_id: str, bucket: str, folder: str):
        return extract_paths(aws_conn_id=aws_conn_id,bucket=bucket, folder=folder)

    @task
    def clean_data(file_paths: dict[str, str], aws_conn_id: str, bucket: str, folder: str):
        return clean_dfs(file_paths=file_paths, aws_conn_id=aws_conn_id, bucket=bucket, folder=folder)

    @task
    def merge_sales_product_data(file_paths: dict[str, str], aws_conn_id: str, bucket: str, folder: str):
        return sales_product_merge(file_paths=file_paths, aws_conn_id=aws_conn_id, bucket=bucket, folder=folder)

    @task
    def enrich_merged_data(file_path: str, aws_conn_id: str, bucket: str, folder: str):
        return enrich_merged_sales_product(file_path=file_path, aws_conn_id=aws_conn_id, bucket=bucket, folder=folder)

    @task
    def hourly_sales_trend_data(file_path: str, aws_conn_id: str, bucket: str, folder: str):
        return hourly_sales_trend(file_path=file_path, aws_conn_id=aws_conn_id, bucket=bucket, folder=folder)

    @task
    def sales_product_trend_data(file_path: str, aws_conn_id: str, bucket: str, folder: str):
        return sales_product_trend(file_path=file_path, aws_conn_id=aws_conn_id, bucket=bucket, folder=folder)

    @task
    def seasonal_sales_patterns_data(file_path: str, aws_conn_id: str, bucket: str, folder: str):
        return seasonal_sales_pattern(file_path=file_path, aws_conn_id=aws_conn_id, bucket=bucket, folder=folder)

    @task
    def revenue_concentration_data(file_path: str, aws_conn_id: str, bucket: str, folder: str):
        return revenue_concentration(file_path=file_path, aws_conn_id=aws_conn_id, bucket=bucket, folder=folder)






    raw_data_paths = extract_raw_data(aws_conn_id=AWS_CONN_ID, bucket=BUCKET_NAME, folder=RAW_DATA_FOLDER)
    cleaned_data_paths = clean_data(
        file_paths=raw_data_paths,
        aws_conn_id=AWS_CONN_ID,
        bucket=BUCKET_NAME,
        folder=PROCESSED_DATA_FOLDER
    )

    merged_df = merge_sales_product_data(
        file_paths=cleaned_data_paths,
        aws_conn_id=AWS_CONN_ID,
        bucket=BUCKET_NAME,
        folder=PROCESSED_DATA_FOLDER
    )

    enriched_merged_df = enrich_merged_data(
        file_path=merged_df,
        aws_conn_id=AWS_CONN_ID,
        bucket=BUCKET_NAME,
        folder=PROCESSED_DATA_FOLDER
    )

    hourly_sales_trend_df = hourly_sales_trend_data(
        file_path=enriched_merged_df,
        aws_conn_id=AWS_CONN_ID,
        bucket=BUCKET_NAME,
        folder=PROCESSED_DATA_FOLDER
    )

    sales_product_trend_df = sales_product_trend_data(
        file_path=enriched_merged_df,
        aws_conn_id=AWS_CONN_ID,
        bucket=BUCKET_NAME,
        folder=PROCESSED_DATA_FOLDER
    )

    seasonal_sales_patterns_df = seasonal_sales_patterns_data(
        file_path=enriched_merged_df,
        aws_conn_id=AWS_CONN_ID,
        bucket=BUCKET_NAME,
        folder=PROCESSED_DATA_FOLDER
    )

    revenue_concentration_df = revenue_concentration_data(
        file_path=enriched_merged_df,
        aws_conn_id=AWS_CONN_ID,
        bucket=BUCKET_NAME,
        folder=PROCESSED_DATA_FOLDER
    )

etl_pipline()