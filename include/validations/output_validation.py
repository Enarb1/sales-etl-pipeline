import pandas as pd
from pandera.errors import SchemaErrors

from include.validations.output_schemas import SALES_OUTPUT_SCHEMA, PRODUCTS_OUTPUT_SCHEMA, \
    MERGED_SALES_PRODUCTS_OUTPUT_SCHEMA, MERGED_DF_ENRICHED_OUTPUT_SCHEMA, PEAKS_OUTPUT_SCHEMA, \
    SALES_PRODUCT_TRENDS_OUTPUT_SCHEMA, SEASONAL_PATTERNS_OUTPUT_SCHEMA, REVENUE_CONCENTRATION_OUTPUT_SCHEMA
from include.config.logger import set_up_logger


logging = set_up_logger(__name__)

SCHEMAS = {
    'sales_north': SALES_OUTPUT_SCHEMA,
    'product_metadata': PRODUCTS_OUTPUT_SCHEMA,
    'merged_sales_product': MERGED_SALES_PRODUCTS_OUTPUT_SCHEMA,
    'merged_sales_product_enriched': MERGED_DF_ENRICHED_OUTPUT_SCHEMA,
    'hourly_sales_trend': PEAKS_OUTPUT_SCHEMA,
    'sales_product_trend': SALES_PRODUCT_TRENDS_OUTPUT_SCHEMA,
    'seasonal_sales_pattern': SEASONAL_PATTERNS_OUTPUT_SCHEMA,
    'revenue_concentration': REVENUE_CONCENTRATION_OUTPUT_SCHEMA
}

def validate_output(df: pd.DataFrame, file_name: str):
    """
    Validation output data, using schema mapper.
    Return validated dataframe on success or raise error on failure.
    """

    if file_name not in SCHEMAS.keys():
        raise KeyError(f'File {file_name} has no output validation schema')

    schema = SCHEMAS[file_name]

    try:
        validated_df = schema.validate(df, lazy=True)
        logging.info(f'File {file_name} validated successfully on output')
        return validated_df
    except SchemaErrors as e:
        failure_cases = e.failure_cases
        logging.error(f'Validation failed for {file_name}: {len(failure_cases)} rows have validation issues')

        raise
