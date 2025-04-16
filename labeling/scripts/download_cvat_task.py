import time
import argparse
from pathlib import Path

from cvat_sdk import make_client


def export_task_to_coco(cvat_host, cvat_username, cvat_password, task_id, output_dir):
    """
    Export a CVAT task to COCO format and save to local directory.
    
    Args:
        cvat_host (str): CVAT server URL (e.g., 'http://localhost:8080')
        cvat_username (str): CVAT username
        cvat_password (str): CVAT password
        task_id (int): ID of the task to export
        output_dir (str): Local directory to save the exported files
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    with make_client(cvat_host, credentials=(cvat_username, cvat_password)) as client:
        print(f"Connected to CVAT server: {cvat_host}")
        
        task = client.tasks.retrieve(task_id)
        print(f"Found task: {task.name} (ID: {task.id})")
        
        output_filename = f"task_{task_id}_coco"
        export_format = "COCO 1.0"
        
        print(f"Exporting task {task_id} to {export_format} format...")
        client.tasks.retrieve(task_id).export_data(
            format_name=export_format,
            filename=output_filename,
            server_files_path=output_dir
        )
        
        print("Waiting for export to complete...")
        while True:
            status = client.tasks.retrieve(task_id).get_export_status()
            if status.value == 'completed':
                print("Export completed successfully!")
                break
            elif status.value == 'failed':
                raise Exception("Export failed")
            time.sleep(1)
    
        exported_file = Path(output_dir) / f"{output_filename}.zip"
        print(f"Exported file saved to: {exported_file}")
        
        return str(exported_file)


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--cvat_host', type=str)
    parser.add_argument('--cvat_username', type=str)
    parser.add_argument('--cvat_password', type=str)
    parser.add_argument('--task_id', type=int)
    parser.add_argument('--output_dir', type=str)

    return parser.parse_args()


# Example usage
if __name__ == "__main__":
    args = parse_args()
    
    exported_file = export_task_to_coco(
        args.cvat_host,
        args.cvat_username,
        args.cvat_password,
        args.task_id,
        args.output_dir,
    )