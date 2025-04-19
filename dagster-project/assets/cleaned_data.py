import os
import shutil
from pathlib import Path
from uuid import uuid4

import dagster as dg
from qdrant_client import QdrantClient
from qdrant_client.http import models

from assets.collected_data import merged_data_dir, merged_parsed_data
from ops.encode_image import encode_image


cleaned_data_path = 'data/cleaned_data'


@dg.asset(deps=[merged_parsed_data])
def cleaned_data(context: dg.AssetExecutionContext):
    source_dir = Path(merged_data_dir)
    target_dir = Path(cleaned_data_path)
    collection_name = 'dataset_images'

    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    
    os.makedirs(target_dir)

    qdrant_client = QdrantClient(host='localhost', port=6333)

    for img_path in source_dir.rglob('*.jpg'):
        img_embedding = encode_image(str(img_path))
        
        if img_embedding is None:
            context.log.error(f'Failed to encode image: {img_path}')
            continue

        search_result = qdrant_client.search(
            collection_name=collection_name,
            query_vector=img_embedding.tolist(),
            limit=1,
        )

        if search_result[0].score > 22:
            shutil.copy(str(img_path), target_dir)

            qdrant_client.upsert(
                collection_name=collection_name,
                points=[
                    models.PointStruct(
                        id=uuid4().int,
                        vector=img_embedding.tolist(),
                    )
                ]
            )

        


