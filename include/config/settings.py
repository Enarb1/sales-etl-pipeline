import yaml

from pathlib import Path

CONFIG_PATH = Path(__file__).parent / 'config.yaml'

def load_config():
    """
    Loading the config.yaml file with the AWS and Snowflake credentials.
    """
    with open(CONFIG_PATH, 'r') as f:
        config = yaml.safe_load(f)

    if not isinstance(config, dict):
        raise ValueError(f'Invalid config file. File in {CONFIG_PATH} is empty.')

    return config

CONFIG = load_config()

AWS_CONN_ID = CONFIG['aws']['conn_id']
BUCKET_NAME = CONFIG['aws']['bucket_name']

PREFIX = CONFIG['aws']['prefix']
RAW_DATA_FOLDER = PREFIX + CONFIG['aws']['folders']['raw_data']
PROCESSED_DATA_FOLDER = PREFIX + CONFIG['aws']['folders']['processed_data']


