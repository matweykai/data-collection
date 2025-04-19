import dagster as dg

from assets.collected_data import collected_data_from_dogtime, collected_data_from_dogs_in_depth, merged_parsed_data


defs = dg.Definitions(
    assets=[
        collected_data_from_dogtime,
        collected_data_from_dogs_in_depth,
        merged_parsed_data
    ],
)