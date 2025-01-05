from cvat_sdk import make_client
import os

def upload_task(user, password, task_name, project_id, images_dir, annotations_path, annotations_format):
    with make_client(host="https://app.cvat.ai/", credentials=(user, password)) as client:
        task_spec = {"name": task_name, "project_id": project_id}
        resources = [os.path.join(images_dir, f) for f in os.listdir(images_dir)]

        task = client.tasks.create_from_data(
            spec=task_spec,
            resource_type="local",
            resources=resources,
            annotation_path=annotations_path,
            annotation_format=annotations_format,
        )
