from cvat_sdk import make_client, models
from cvat_sdk.core.proxies.tasks import ResourceType, Task
import os
import shutil

def remove_folder_and_contents(folder_path):
    try:
        shutil.rmtree(folder_path)
        print(f"Folder and its contents removed: {folder_path}")
    except OSError as e:
        print(f"Error: {e}")

def upload_task(user,password,task_name,project_id,images_dir,annotations_dir,annotations_format):
    with make_client(host="https://app.cvat.ai/", credentials=(user, password)) as client:

        task_spec = {
            "name": task_name,
            "project_id" : project_id
        }
        # List all entries in the directory and get their full paths
        full_paths = [os.path.join(images_dir, entry) for entry in os.listdir(images_dir)]

        task = client.tasks.create_from_data(
            spec=task_spec,
            resource_type=ResourceType.LOCAL,
            resources=full_paths,
            annotation_path=annotations_dir,
            annotation_format=annotations_format
        )

    
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    labels_dir = "assets/frames"
    import datetime
    task_name = datetime.datetime.today().strftime('%Y%m%d')
    print(f"Uploading task from {labels_dir}")
    upload_task(os.environ["CVAT_USER"],os.environ["CVAT_PASSWORD"],
                task_name=task_name,
                project_id=int(os.environ["CVAT_PROJECT_ID"]),
                images_dir=labels_dir +"/images/train",
                annotations_dir=labels_dir +"/labels.zip",
                annotations_format="YOLOv8 Detection 1.0")
    print("Labels uploaded")
    # remove_folder_and_contents(labels_dir)