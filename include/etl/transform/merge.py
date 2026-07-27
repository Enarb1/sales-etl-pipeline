import pandas as pd

from include.config.logger import set_up_logger
from include.utils.s3_utils import get_s3hook_and_storage_options
from include.utils.dataframe_utils import read_df, load_df_to_s3, get_file_name
from include.validations.output_validation import validate_output

logging = set_up_logger(__name__)

def merge_df(df1: pd.DataFrame, df2: pd.DataFrame, how: str = 'inner', on: str = None,**kwargs) -> pd.DataFrame:
    """
    Merge two Dataframes. Returns merged dataframe. Inner merge is set by default.
    """
    merged_df = pd.merge(df1, df2, how=how, on=on, **kwargs)
    logging.info(f'Merge successful. Table with {len(merged_df)} rows and {len(merged_df.columns)} columns')
    return merged_df

def sales_product_merge(file_paths: dict[str, str], aws_conn_id, bucket: str, folder: str) -> str:
    """
    Sales North and Product Metadata dataframes are merged by product_id.
    Validating the new merged dataframe. Loading the new dataframe to S3.
    Returns the S3 path of the new merged dataframe.
    """
    _, storage_options = get_s3hook_and_storage_options(aws_conn_id=aws_conn_id)

    sales_df = read_df(file_paths['sales_north_cleaned'], storage_options=storage_options)
    product_df = read_df(file_paths['product_metadata_cleaned'], storage_options=storage_options)

    logging.info('Merging tables.. ')
    merged_sales_product_df = merge_df(df1=sales_df, df2=product_df, on='product_id')

    file_name = 'merged_sales_product'
    s3_path = f"s3://{bucket}/{folder}{file_name}.parquet"

    logging.info(f'{merged_sales_product_df.info()}')
    validated_merged_df = validate_output(df=merged_sales_product_df, file_name=file_name)

    load_df_to_s3(df=validated_merged_df, s3_path=s3_path, storage_options=storage_options)

    return s3_path


def enrich_merged_sales_product(file_path: str, aws_conn_id: str, bucket: str, folder: str) -> str:
    """
    Adding new column to merged_sales_product. New columns: month, week, weekday, hour, sales_bucket.
    Validating the updated merged_sales_product dataframe Loading the dataframe as new file to S3.
    Returns the S3 path of the new dataframe.
    """
    _, storage_options = get_s3hook_and_storage_options(aws_conn_id=aws_conn_id)
    merged_df = read_df(file_path, storage_options=storage_options)

    initial_cols = len(merged_df.columns)
    logging.info('Adding new columns to merged_sales_product....')

    merged_df['timestamp'] = pd.to_datetime(merged_df['timestamp'], format='mixed', errors='coerce')
    merged_df['month'] = merged_df['timestamp'].dt.to_period('M').astype(str)
    logging.info('Added Month column to merged_sales_product.')

    merged_df['week'] = merged_df['timestamp'].dt.isocalendar().week
    logging.info('Added Week column to merged_sales_product')

    merged_df['weekday'] = merged_df['timestamp'].dt.day_name()
    logging.info('Added Weekday column to merged_sales_product')

    merged_df['hour'] = merged_df['timestamp'].dt.hour.astype('Int64')
    logging.info('Added hour column to merged_sales_product')

    merged_df['sales_bucket'] = pd.cut(
        merged_df['total_sales'],
        bins=[0, 100, 500, float('inf')],
        labels=['Low', 'Medium', 'High']
    )
    logging.info('Added sales bucket column to merged_sales_product')

    logging.info(f'Successfully added {len(merged_df.columns) - initial_cols} new columns.')

    file_name = f'{get_file_name(file_path)}_enriched'
    logging.info(f'New file name created: {file_name}')

    logging.info(f'Validating {file_name}')
    validated_enriched_df = validate_output(df=merged_df, file_name=file_name)

    s3_path = f"s3://{bucket}/{folder}{file_name}.parquet"
    load_df_to_s3(df=validated_enriched_df,s3_path=s3_path, storage_options=storage_options, index=False)

    return s3_path