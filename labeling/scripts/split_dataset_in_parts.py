import argparse
from shutil import copy
from pathlib import Path


def main(raw_images_dir: str, tasks_base_dir: str, tasks_count: int, cross_task_fraq: float):
    imgs_path_list = [path for path in Path(raw_images_dir).iterdir()]

    task_size = round(len(imgs_path_list) / tasks_count) + 1
    cross_task_size = round(task_size * cross_task_fraq)

    global_index = 0

    for task_ind in range(tasks_count):
        task_path = Path(tasks_base_dir) / f'task_{task_ind}'
        task_path.mkdir(parents=True, exist_ok=True)

        for _ in range(task_size):
            if global_index >= len(imgs_path_list):
                break

            src_img_path = imgs_path_list[global_index]
            dst_img_path = task_path / src_img_path.name

            copy(src_img_path, dst_img_path)
            global_index += 1

        for extra_index in range(cross_task_size):
            src_img_path = imgs_path_list[(global_index + extra_index) % len(imgs_path_list)]
            dst_img_path = task_path / src_img_path.name

            copy(src_img_path, dst_img_path)


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--raw_images_dir', type=str)
    parser.add_argument('--tasks_base_dir', type=str)
    parser.add_argument('--tasks_count', type=int)
    parser.add_argument('--cross_task_fraq', type=float)

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    main(args.raw_images_dir, args.tasks_base_dir, args.tasks_count, args.cross_task_fraq)
