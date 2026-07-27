import pandas as pd

from include.utils.s3_utils import get_s3hook_and_storage_options
from include.utils.dataframe_utils import read_df, load_df_to_s3
from include.validations.input_validation import validate_input
from include.validations.output_validation import validate_output
from include.config.logger import set_up_logger

logging = set_up_logger(__name__)

def product_metadata_clean(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleaning product metadata dataframe.
    Transforming 'brand' column to uppercase and 'category' column to lowercase.
    Dropping duplicate rows and rows with NaN values in 'product_id' and 'rating' columns.
    returning cleaned dataframe.
    """
    df =  df.copy()

    df['brand'] = df['brand'].str.strip().str.upper()
    df['category'] = df['category'].str.strip().str.lower()
    df.dropna(subset=['product_id', 'rating'], inplace=True)
    df.drop_duplicates(subset='product_id', inplace=True)

    return df


def sales_north_clean(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleaning sales north dataframe. Dropping rows with NaN values in 'region' and 'timestamp' columns.
    Dropping rows with NaN values or less than or equal to 0 in 'price' and 'quantity 'columns.
    Timestamp column to datetime format. Computing the total_sales.
    Returning cleaned dataframe.
    """
    df = df.copy()

    invalid_price_qty_mask = (df[['price', 'quantity']].isna() | df[['price', 'quantity']].le(0)).any(axis=1)

    df['region'] = df['region'].str.strip().str.lower()
    df.dropna(subset=['region', 'timestamp'], inplace=True)
    df = df[~invalid_price_qty_mask].copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed', errors='coerce')
    df['total_sales'] = df['price'] * df['quantity']

    return df

def columns_to_snake_case(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforms columns to snake case. Returns a dataframe with the transformed columns.
    """
    df = df.copy()

    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

    logging.info(f'All columns transformed to snake case: {df.columns}')

    return df

def clean_dfs(file_paths: dict[str, str], aws_conn_id: str, bucket: str, folder: str):
    """
    Cleaning Dataframes. Validating on input.
    Getting cleaning logic from a mapper dictionary and cleaning columns.
    Validating output and loadin to the Processed Folder in S3.
    Returning a dictionary with the cleaned dataframe paths in S3.
    """
    _, storage_options = get_s3hook_and_storage_options(aws_conn_id=aws_conn_id)

    cleaner_func_mapper =  {
        'sales_north': sales_north_clean,
        'product_metadata': product_metadata_clean,
    }
    logging.info('Cleaning DataFrames...')
    cleaned_dfs_paths = {}

    for file_name, s3_path in file_paths.items():

        if file_name not in cleaner_func_mapper:
            logging.info(f'Skipping {file_name} because there is no cleaning logic for it')
            continue

        logging.info(f'Cleaning {file_name}...')
        df = read_df(file_path=s3_path, storage_options=storage_options)

        logging.info(f'Validating on input {file_name}')
        df = validate_input(df=df, file_name=file_name)

        logging.info(f'Cleaning {file_name}...')
        df = cleaner_func_mapper[file_name](df=df)
        validated_df = validate_output(df=df, file_name=file_name)

        cleaned_file_name = f'{file_name}_cleaned'
        s3_path = f"s3://{bucket}/{folder}{cleaned_file_name}.parquet"

        logging.info(f'{validated_df.info()}')
        load_df_to_s3(df=validated_df, s3_path=s3_path, storage_options=storage_options, index=False)

        cleaned_dfs_paths[cleaned_file_name] = s3_path

    return cleaned_dfs_paths
