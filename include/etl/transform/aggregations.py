import pandas as pd

from include.config.logger import set_up_logger
from include.utils.s3_utils import get_s3hook_and_storage_options
from include.utils.dataframe_utils import read_df, load_df_to_s3
from include.validations.output_validation import validate_output

logging = set_up_logger(__name__)

def hourly_sales_trend(file_path: str, aws_conn_id: str, bucket: str, folder: str) -> str:
    """
    Hourly sales trend aggregation.
    Identifies the peak sales hours for each region by aggregating sales data on an hourly basis.
    Returns S3 path.
    """
    _, storage_options = get_s3hook_and_storage_options(aws_conn_id=aws_conn_id)
    enriched_merged_df = read_df(file_path, storage_options=storage_options)

    logging.info('Starting aggregations foe hourly_sales_trend')

    agg = (
            enriched_merged_df
           .groupby(['region', 'category', 'hour'], as_index=False)
           .agg(hourly_sales_trend=('total_sales', 'sum'))
           )
    logging.info('Aggregated a table, grouped by region, category, hour with a new column hourly_sales_trend')

    idx = agg.groupby(['region', 'category'])['hourly_sales_trend'].idxmax()
    logging.info(
        'Grouped the aggregated table by region and category '
        'and taking the index of the max value of hourly_sales_trend for each category'
    )


    peaks = agg.loc[idx].reset_index(drop=True)
    logging.info('Got the peak hours for each category and region')

    file_name = hourly_sales_trend.__name__
    logging.info(f'New file name created: {file_name}')

    logging.info(f'Validating {file_name}')
    validated_peaks = validate_output(df=peaks, file_name=file_name)

    s3_path = f"s3://{bucket}/{folder}{file_name}.parquet"

    logging.info(f'Loading {file_name} to S3')
    load_df_to_s3(df=validated_peaks, s3_path=s3_path, storage_options=storage_options, index=False)

    return s3_path


def sales_product_trend(file_path: str, aws_conn_id: str, bucket: str, folder: str) -> str:
    """
    Evaluates and ranks products based on both their revenue contribution and sales frequency.
    Classifies products into performance buckets such as "Bestseller", "Average" and "Low Performer".
    Returns S3 path.
    """
    # TODO add the reading of a df into a reusable function
    _, storage_options = get_s3hook_and_storage_options(aws_conn_id=aws_conn_id)
    enriched_merged_df = read_df(file_path, storage_options=storage_options)

    file_name = sales_product_trend.__name__
    logging.info(f'New file name created: {file_name}')

    summary = (
                enriched_merged_df
               .groupby(['product_id', 'category', 'brand', 'rating'], as_index=False)
                .agg(
                    revenue=('total_sales', 'sum'),
                    sales_count=('product_id', 'size')
                )
    )
    logging.info('Created summary table.')

    revenue_rank = summary['revenue'].rank(method='average', pct=True)
    sales_count_rank = summary['sales_count'].rank(method='average', pct=True)

    performance_score = revenue_rank * 0.50 + sales_count_rank * 0.50

    logging.info('Performance score calculated')

    summary['value_bucket'] = pd.cut(
        performance_score,
        bins=[0, 0.20, 0.50, 1],
        labels=['Low Performer', 'Average', 'Bestseller'],
        include_lowest=True
    )

    logging.info('Value bucket added to the summary table')

    validated_summary = validate_output(df=summary, file_name=file_name)
    # TODO make a separate function, which builds the path
    s3_path = f"s3://{bucket}/{folder}{file_name}.parquet"
    load_df_to_s3(df=validated_summary, s3_path=s3_path, storage_options=storage_options, index=False)

    return s3_path


def seasonal_sales_pattern(file_path: str, aws_conn_id: str, bucket: str, folder: str) -> str:
    """
    Analyzes how sales vary on a quarterly basis
    and how different product categories perform in each quarter.
    Returns S3 path.
    """
    _, storage_options = get_s3hook_and_storage_options(aws_conn_id=aws_conn_id)
    seasonal_df = read_df(file_path, storage_options=storage_options)

    file_name = seasonal_sales_pattern.__name__

    seasonal_df['timestamp'] = pd.to_datetime(seasonal_df['timestamp'], format='mixed', errors='coerce')
    seasonal_df['quarter'] = seasonal_df['timestamp'].dt.to_period('Q').astype(str)
    logging.info('Added Quarter column')
    seasonal_patterns = (
        seasonal_df
        .groupby(['quarter', 'category'], as_index=False).agg(
        total_sales=('total_sales', 'sum'),
        )
    )
    logging.info('Seasonal patterns dataframe created')

    validated_seasonal_patterns = validate_output(df=seasonal_patterns, file_name=file_name)

    s3_path = f"s3://{bucket}/{folder}{file_name}.parquet"
    load_df_to_s3(df=validated_seasonal_patterns, s3_path=s3_path, storage_options=storage_options, index=False)

    return s3_path


def revenue_concentration(file_path: str, aws_conn_id: str, bucket: str, folder: str) -> str:
    """
    Examines how revenue is distributed across regions and measures the concentration of sales.
    This task calculates each region’s revenue share and computes a basic inequality metric .
    Returns S3 path.
    """
    _, storage_options = get_s3hook_and_storage_options(aws_conn_id=aws_conn_id)
    enriched_df = read_df(file_path, storage_options=storage_options)

    file_name = revenue_concentration.__name__

    summary = (
                enriched_df.
               groupby(['region'], as_index=False)
                .agg(
                    region_revenue=('total_sales', 'sum'),
                )
                .sort_values('region_revenue', ascending=False)
                .reset_index(drop=True)
    )
    logging.info('Summary dataframe aggregated')

    total = summary['region_revenue'].sum()
    logging.info(f'Total revenue calculated: {total}')

    if total <= 0:
        raise ValueError('Total revenue cannot be less than or equal to 0')

    summary['revenue_share'] = summary['region_revenue'] / total
    logging.info('Revenue shares calculated')

    summary['cumulative_share'] = summary['revenue_share'].cumsum()
    logging.info('Cumulative shares calculated')

    validated_summary = validate_output(df=summary, file_name=file_name)
    s3_path = f"s3://{bucket}/{folder}{file_name}.parquet"
    load_df_to_s3(df=validated_summary, s3_path=s3_path, storage_options=storage_options, index=False)

    return s3_path




