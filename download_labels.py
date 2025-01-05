from cvat_sdk import make_client, models
from cvat_sdk.core.proxies.tasks import ResourceType, Task
import os
import shutil


def download_finished_tasks(user,password,task_name,project_id,images_dir,annotations_dir,annotations_format):
    with make_client(host="https://app.cvat.ai/", credentials=(user, password)) as client:
        for c in client.tasks.list():
            if c.status == "completed":
                print(len(c.get_frames_info()))
                total_frames = len(c.get_frames_info())
                # c.export_dataset(format_name=annotations_format,filename="result.zip",include_images=False)
                c.download_frames(range(total_frames),outdir="results")
                print(c.get_annotations())
        

    
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    labels_dir = "assets/frames"
    import datetime
    task_name = datetime.datetime.today().strftime('%Y%m%d')
    print(f"Uploading task from {labels_dir}")
    download_finished_tasks(os.environ["CVAT_USER"],os.environ["CVAT_PASSWORD"],
                task_name=task_name,
                project_id=int(os.environ["CVAT_PROJECT_ID"]),
                images_dir=labels_dir +"/images/train",
                annotations_dir=labels_dir +"/labels.zip",
                annotations_format="YOLOv8 Detection 1.0")
    print("Labels uploaded")
