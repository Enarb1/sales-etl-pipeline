import pandas as pd
from pandera.errors import SchemaErrors

from include.validations.input_schemas import SALES_INPUT_SCHEMA, PRODUCTS_INPUT_SCHEMA
from include.config.logger import set_up_logger


logging = set_up_logger(__name__)

SCHEMAS = {
    'sales_north': SALES_INPUT_SCHEMA,
    'product_metadata': PRODUCTS_INPUT_SCHEMA,
}



def get_failure_summary(failure_cases) -> pd.DataFrame:
    """
    Creating a failure summary from the failure cases and returning a dataframe with the information.
    """
    failure_cases = failure_cases.copy()

    failure_cases['value_type_fails'] = failure_cases['failure_case'].map(lambda v: type(v).__name__)
    failure_summary = (
        failure_cases
        .groupby(
            ['column', 'check', 'value_type_fails'],dropna=False
        ).size()
        .reset_index(name='affected_rows')
        .sort_values(by='affected_rows', ascending=False))

    return failure_summary


def validate_input(df: pd.DataFrame, file_name: str) -> pd.DataFrame:
    """
    Validates the data in input. Gets the schema from the schema maper. Logs errors and returns the DataFrame.
    """
    if file_name not in SCHEMAS.keys():
        raise KeyError(f'No schema found for {file_name}')

    schema = SCHEMAS[file_name]

    try:
        validated_df = schema.validate(df, lazy=True)
        logging.info(f'Successfully validated {file_name}. No errors found.')
        return validated_df
    except SchemaErrors as e:
        failure_cases = e.failure_cases

        logging.error(f'Validation failed for {file_name}: {len(failure_cases)} rows have validation issues')

        failure_summary = get_failure_summary(failure_cases)

        logging.error(f'Validation failed for {file_name}: \n{failure_summary.to_string(index=False)}')

        return df