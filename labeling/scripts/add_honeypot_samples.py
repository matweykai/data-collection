import argparse
from shutil import copy
from pathlib import Path
from random import sample


def main(task_imgs_dir: str, gt_imgs_dir: str, honeypots_count: int):
    task_imgs_dir = Path(task_imgs_dir)
    gt_imgs_dir = Path(gt_imgs_dir)

    potential_honeypots = list(gt_imgs_dir.glob('*.jpg'))

    for img_path in sample(potential_honeypots, honeypots_count):
        dst_img_path = task_imgs_dir / img_path.name
        copy(img_path, dst_img_path)


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--task_imgs_dir', type=str)
    parser.add_argument('--gt_imgs_dir', type=str)
    parser.add_argument('--honeypots_count', type=int)

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    main(args.task_imgs_dir, args.gt_imgs_dir, args.honeypots_count)
