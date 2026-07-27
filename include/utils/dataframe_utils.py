import pandas as pd
from pathlib import PurePosixPath
from include.config.logger import set_up_logger


logging = set_up_logger(__name__)


def get_file_name(s3_path: str) -> str:
    """
    Getting the file name from a S3 Path.
    """
    logging.info(f'Getting file name from {s3_path}')
    return s3_path.split('/')[-1].split('.')[0]

def get_file_type(s3_path: str) -> str:
    """
    Returning the file type from a path.
    """
    logging.info(f'Getting file type from {s3_path}')
    return PurePosixPath(s3_path).suffix.lower().strip('.')


def load_df_to_s3(df: pd.DataFrame, s3_path: str, storage_options: dict, **kwargs) -> None:
    """
    Loading dataframe into S3 bucket. Using a mapper dictionary to choose a load method.
    """

    loader = {
        'csv': df.to_csv,
        'parquet': df.to_parquet,
        'json': df.to_json,
    }

    logging.info(f'Loading dataframe to {s3_path}')

    file_type = get_file_type(s3_path)

    if file_type not in loader:
        raise KeyError(f'File type {file_type} not supported. Can not load dataframe to {s3_path}')

    try:
        loader[file_type](s3_path, storage_options=storage_options, **kwargs)
        logging.info(f'Successfully loaded dataframe to {s3_path}')
    except Exception as e:
        logging.error(f'Failed to load dataframe to {s3_path}')
        raise e


def read_df(file_path: str, storage_options: dict, **kwargs) -> pd.DataFrame:
    """
    Reading data from S3 Path. Returning Pandas DataFrame.
    """
    readers = {
        'csv': pd.read_csv,
        'parquet': pd.read_parquet,
        'json': pd.read_json,
    }


    file_type = get_file_type(file_path)

    if file_type not in readers:
        raise KeyError(f'Can not read {file_type}.')

    try:
        reader = readers[file_type]
        logging.info(f'Successfully read {file_type} to {file_path}')
    except KeyError:
        raise KeyError(f'File type {file_type} not supported.')

    return reader(file_path, storage_options=storage_options, **kwargs)