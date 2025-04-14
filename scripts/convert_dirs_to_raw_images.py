import os
import shutil
import argparse
from pathlib import Path

from tqdm import tqdm


def main(images_root: str, target_dir: str):
    os.makedirs(target_dir, exist_ok=True)
    images_root = Path(images_root)

    for img_dir in tqdm(Path(images_root).iterdir()):
        for img_path in img_dir.iterdir():
            src_path = str(img_path)
            dst_path = os.path.join(target_dir, f'{images_root.name}__{img_dir.name.lower().strip()}__{img_path.name}')

            try:
                shutil.copy(src_path, dst_path)
            except IsADirectoryError:
                for img_path in img_dir.rglob('*.jpg'):
                    src_path = str(img_path)
                    dst_path = os.path.join(target_dir, f'{images_root.name}__{img_dir.name.lower().strip()}__{img_path.name}')

                    shutil.copy(src_path, dst_path)


def parse_args():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--images_root', type=str)
    parser.add_argument('--target_dir', type=str)

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    main(args.images_root, args.target_dir)
