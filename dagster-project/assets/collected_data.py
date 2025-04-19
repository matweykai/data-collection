import shutil
from pathlib import Path

import dagster as dg

from ops.collect_links import *
from ops.filter_links import *
from ops.parse_sites import *


dogs_time_dir = 'data/dogs_time'
dogs_in_depth_dir = 'data/dogs_in_depth'


@dg.asset
def collected_data_from_dogtime(context: dg.AssetExecutionContext):
    context.log.info('Collecting links from dogtime')
    dogtime_links = collect_links_from_dogstime()
    context.log.info(f'Collected {len(dogtime_links)} links from dogtime')

    context.log.info('Filtering links')
    filtered_links = filter_links(dogtime_links)[:1]
    context.log.info(f'Filtered {len(filtered_links)} links from dogtime')

    if os.path.exists(dogs_time_dir):
        shutil.rmtree(dogs_time_dir)
    
    os.makedirs(dogs_time_dir)

    context.log.info('Parsing links')
    for link in filtered_links:
        parse_dog_time_link(link, dogs_time_dir)
    context.log.info('Finished parsing links')

    context.log.info('Update used links')
    with open('data/used_links.txt', 'at') as file:
        for link in filtered_links:
            file.write(link + '\n')
    context.log.info('Finished updating used links')


@dg.asset
def collected_data_from_dogs_in_depth(context: dg.AssetExecutionContext):
    context.log.info('Collecting links from dogs in depth')
    dogs_in_depth_links = collect_links_from_dogs_in_depth()
    context.log.info(f'Collected {len(dogs_in_depth_links)} links from dogs in depth')

    context.log.info('Filtering links')
    filtered_links = filter_links(dogs_in_depth_links)[:1]
    context.log.info(f'Filtered {len(filtered_links)} links from dogs in depth')

    if os.path.exists(dogs_in_depth_dir):
        shutil.rmtree(dogs_in_depth_dir)
    
    os.makedirs(dogs_in_depth_dir)

    context.log.info('Parsing links')
    for link in filtered_links:
        parse_dogs_in_depth_link(link, dogs_in_depth_dir)
    context.log.info('Finished parsing links')

    context.log.info('Update used links')
    with open('data/used_links.txt', 'at') as file:
        for link in filtered_links:
            file.write(link + '\n')
    context.log.info('Finished updating used links')


@dg.asset(deps=[collected_data_from_dogtime, collected_data_from_dogs_in_depth])
def merged_parsed_data(context: dg.AssetExecutionContext):
    target_dir = Path('data/merged_parsed_data')
    dogs_time_dir_path = Path(dogs_time_dir)
    dogs_in_depth_dir_path = Path(dogs_in_depth_dir)

    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    
    os.makedirs(target_dir)

    context.log.info('Moving data from dogtime')
    for temp_dir in dogs_time_dir_path.iterdir():
        shutil.move(temp_dir, target_dir)

    context.log.info('Moving data from dogs in depth')
    for temp_dir in dogs_in_depth_dir_path.iterdir():
        shutil.move(temp_dir, target_dir)
