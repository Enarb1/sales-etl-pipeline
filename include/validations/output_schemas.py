from pandera import Column, Check, DataFrameSchema, DateTime

GT_ZERO = Check.greater_than(0)

# TODO repeatable checks into variables
SALES_OUTPUT_SCHEMA = DataFrameSchema({
    'sales_id': Column(int, nullable=False),
    'product_id': Column(int, nullable=False),
    'region': Column(str, checks=Check.isin('east', 'west', 'north', 'south'), nullable=False),
    'quantity': Column(int, checks=GT_ZERO, nullable=False),
    'price': Column(float, checks=GT_ZERO, nullable=False),
    'timestamp': Column(DateTime, nullable=False),
    'total_sales': Column(float, checks=GT_ZERO, nullable=False),
}, strict=True)


PRODUCTS_OUTPUT_SCHEMA = DataFrameSchema({
    'product_id': Column(int, nullable=False),
    'category': Column(str, nullable=False, checks=Check(lambda s: s.str.islower())),
    'brand': Column(str, nullable=False, checks=Check(lambda s: s.str.isupper())),
    'rating': Column(float, nullable=False, checks=Check.in_range(1, 5)),
}, strict=True)



MERGED_SALES_PRODUCTS_OUTPUT_SCHEMA = DataFrameSchema({
    'sales_id': Column(int, nullable=False),
    'product_id': Column(int, nullable=False),
    'region': Column(str, checks=Check.isin('east', 'west', 'north', 'south'), nullable=False),
    'quantity': Column(int, checks=GT_ZERO, nullable=False),
    'price': Column(float, checks=GT_ZERO, nullable=False),
    'timestamp': Column(DateTime, nullable=False),
    'total_sales': Column(float, checks=GT_ZERO, nullable=False),
    'category': Column(str, nullable=False, checks=Check(lambda s: s.str.islower())),
    'brand': Column(str, nullable=False, checks=Check(lambda s: s.str.isupper())),
    'rating': Column(float, nullable=False, checks=Check.in_range(1, 5)),
}, strict=True)



MERGED_DF_ENRICHED_OUTPUT_SCHEMA = DataFrameSchema({
    'sales_id': Column(int, nullable=False),
    'product_id': Column(int, nullable=False),
    'region': Column(str, checks=Check.isin('east', 'west', 'north', 'south'), nullable=False),
    'quantity': Column(int, checks=GT_ZERO, nullable=False),
    'price': Column(float, checks=GT_ZERO, nullable=False),
    'timestamp': Column(DateTime, nullable=False),
    'total_sales': Column(float, checks=GT_ZERO, nullable=False),
    'category': Column(str, nullable=False, checks=Check(lambda s: s.str.islower())),
    'brand': Column(str, nullable=False, checks=Check(lambda s: s.str.isupper())),
    'rating': Column(float, nullable=False, checks=Check.in_range(1, 5)),
    'month': Column(str, nullable=False),
    'week': Column('UInt32', nullable=False,),
    'weekday': Column(str, nullable=False,),
    'hour': Column(int, nullable=False,),
    'sales_bucket': Column(str, nullable=False,checks=Check.isin('Low', 'Medium', 'High')),
},strict=True)


PEAKS_OUTPUT_SCHEMA = DataFrameSchema({
    'region': Column(str, nullable=False, checks=Check.isin('east', 'west', 'north', 'south')),
    'category': Column(str, nullable=False, checks=Check(lambda s: s.str.islower())),
    'hour': Column(int, nullable=False,),
    'hourly_sales_trend': Column(float, nullable=False,),
}, strict=True)


SALES_PRODUCT_TRENDS_OUTPUT_SCHEMA = DataFrameSchema({
    'product_id': Column(int, nullable=False),
    'category': Column(str, nullable=False, checks=Check(lambda s: s.str.islower())),
    'brand': Column(str, nullable=False, checks=Check(lambda s: s.str.isupper())),
    'rating': Column(float, nullable=False, checks=Check.in_range(1, 5)),
    'revenue': Column(float, nullable=False, checks=GT_ZERO),
    'sales_count': Column(int, nullable=False, checks=GT_ZERO),
    'value_bucket': Column(str, nullable=False, checks=Check.isin('Low Performer', 'Average', 'Bestseller')),
}, strict=True)


SEASONAL_PATTERNS_OUTPUT_SCHEMA = DataFrameSchema({
    'quarter': Column(str, nullable=False),
    'category': Column(str, nullable=False, checks=Check(lambda s: s.str.islower())),
    'total_sales': Column(float, nullable=False, checks=GT_ZERO),
}, strict=True)


REVENUE_CONCENTRATION_OUTPUT_SCHEMA = DataFrameSchema({
    'region': Column(str, nullable=False),
    'region_revenue': Column(float, nullable=False, checks=GT_ZERO),
    'revenue_share': Column(float, nullable=False, checks=Check.in_range(0, 1)),
    'cumulative_share': Column(float, nullable=False, checks=Check.in_range(0, 1)),
})





