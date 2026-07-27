from pandera import Column, Check, DataFrameSchema


SALES_INPUT_SCHEMA = DataFrameSchema({
    'sales_id': Column(int, nullable=False),
    'product_id': Column(int, nullable=False),
    'region': Column(str),
    'quantity': Column(int, checks=Check.greater_than(0, errors='Value must be greater than 0')),
    'price': Column(float, checks=Check.greater_than(0, errors='Value must be greater than 0')),
    'timestamp': Column('datetime64[us]'),
    'total_sales': Column(float)
}, strict=True)


PRODUCTS_INPUT_SCHEMA = DataFrameSchema({
    'product_id': Column(int, nullable=False),
    'category': Column(str, nullable=False),
    'brand': Column(str, nullable=False),
    'rating': Column(float, nullable=False),
}, strict=True)