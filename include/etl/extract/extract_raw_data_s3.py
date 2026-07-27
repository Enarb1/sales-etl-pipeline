from pathlib import PurePosixPath
from include.config.logger import set_up_logger
from include.utils.s3_utils import get_s3hook_and_storage_options


logging = set_up_logger(__name__)

def extract_paths(aws_conn_id: str, bucket: str, folder: str):
    """
    Extracting S3 paths from a S3 folder.
    """
    logging.info(f'Extracting data from {bucket}/{folder}')

    s3_hook, storage_options = get_s3hook_and_storage_options(aws_conn_id=aws_conn_id)
    keys = s3_hook.list_keys(bucket_name=bucket, prefix=folder)

    logging.info(f'{len(keys)} files found in {bucket}/{folder}')

    if not keys:
        raise Exception(f'No keys found for {bucket}/{folder}')
    logging.info(f'Found {len(keys)} keys for {bucket}/{folder}')

    file_paths = {}
    supported_file_types = ['.csv', '.json', '.parquet']

    for key in keys:
        path = PurePosixPath(key)
        extension = path.suffix.lower()

        if extension not in supported_file_types:
            logging.warning(f'File type {extension} not supported')
            continue

        s3_path = f"s3://{bucket}/{key.lstrip('/')}"
        df_name = path.stem.lower()

        if df_name in file_paths.keys():
            raise ValueError(f'File {df_name} already exists in {bucket}/{folder}')

        file_paths[df_name] = s3_path

    if not file_paths:
        raise Exception(f'No files found in {bucket}/{folder}')

    return file_paths