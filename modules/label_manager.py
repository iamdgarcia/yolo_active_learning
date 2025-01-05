
from cvat_sdk import make_client, models
from cvat_sdk.core.proxies.tasks import ResourceType, Task
import os
import sys
import shutil


def download_finished_tasks(user,password,annotations_format):
    with make_client(host="https://app.cvat.ai/", credentials=(user, password)) as client:
        for c in client.tasks.list():
            if c.status == "completed":
                c.export_dataset(format_name=annotations_format,filename=f"{c.name}.zip",include_images=False)
        

def list_files(folder_path):
    """Lists all files in a given folder."""
    try:
        # Extract file names without extensions
        return {os.path.splitext(file)[0] for file in os.listdir(folder_path)}
    except FileNotFoundError:
        print(f"Error: The folder {folder_path} does not exist.")
        sys.exit(1)

def compare_and_remove(root_path):
    """Compare files in two folders and remove files from ROOT_PATH/images/train that are not in ROOT_PATH/labels/train."""
    images_path = os.path.join(root_path, "images/Train")
    labels_path = os.path.join(root_path, "labels/Train")

    # List files in both folders (ignoring extensions)
    files_in_images = list_files(images_path)
    files_in_labels = list_files(labels_path)

    # Find files in images that are not in labels
    unique_to_images = files_in_images - files_in_labels

    # List the unique files
    if unique_to_images:
        print("Files in images/train but not in labels/train:")
        for file in unique_to_images:
            print(file)

        # Remove the unique files (with any extensions)
        for file in unique_to_images:
            matching_files = [f for f in os.listdir(images_path) if os.path.splitext(f)[0] == file]
            for matching_file in matching_files:
                file_path = os.path.join(images_path, matching_file)
                try:
                    os.remove(file_path)
                    print(f"Removed: {file_path}")
                except OSError as e:
                    print(f"Error removing {file_path}: {e}")
    else:
        print("No files to remove. Both folders have the same files.")