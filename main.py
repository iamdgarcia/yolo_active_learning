import logging
import os
import traceback
from dotenv import load_dotenv
from download_yt_videos import search_and_download_yt_dlp
from fix_video_format import process_videos_in_folder
from process_video import setup_directories_and_yaml, process_videos, compress_folder
from upload_labels import upload_task
from download_labels import download_finished_tasks
from clear_empty_labels import compare_and_remove
import yaml
import json
from datetime import datetime

# Log file setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("pipeline.log"),
    ],
)

def load_config(config_path="config.yaml"):
    """Load configuration from a YAML file."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    with open(config_path, "r") as file:
        return yaml.safe_load(file)

def load_last_execution(file_path="last_execution.json"):
    """Load the last execution details."""
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return json.load(file)
    return {}

def save_last_execution(step_name, status, file_path="last_execution.json"):
    """Save the execution status of a step."""
    last_execution = load_last_execution(file_path)
    last_execution["last_run"] = datetime.now().isoformat()
    last_execution["steps"] = last_execution.get("steps", {})
    last_execution["steps"][step_name] = status

    with open(file_path, "w") as file:
        json.dump(last_execution, file, indent=4)

def main():
    
    # Load environment variables and configuration
    try:
        load_dotenv()
        config = load_config("config.yaml")
        last_execution = load_last_execution()
        
        task_name = config["cvat"]["task_name"]
        if task_name == "auto":
            import datetime
            task_name = datetime.datetime.today().strftime('%Y%m%d')
        output_path = config["paths"]["output"] + f"/{task_name}"
        
        logging.info(f"Last Execution: {last_execution}")
    except Exception as e:
        logging.error(f"Failed to load configuration or execution data: {e}")
        traceback.print_exc()
        return

    # Step 1: Download YouTube Videos
    if config["steps"]["download_videos"]["enabled"]:
        try:
            logging.info("Step 1: Downloading YouTube Videos...")
            queries = config["youtube"]["queries"]
            num_videos = config["youtube"]["num_videos"]
            resolution = config["youtube"]["resolution"]
            search_and_download_yt_dlp(queries, num_results=num_videos, resolution=resolution)
            save_last_execution("download_videos", "success")
        except Exception as e:
            logging.error(f"Error in Step 1: {e}")
            save_last_execution("download_videos", "failure")
            traceback.print_exc()
            return

    # Step 2: Fix Video Format
    if config["steps"]["fix_video_format"]["enabled"]:
        try:
            logging.info("Step 2: Fixing Video Format...")
            process_videos_in_folder(folder_path=config["paths"]["downloads"])
            save_last_execution("fix_video_format", "success")
        except Exception as e:
            logging.error(f"Error in Step 2: {e}")
            save_last_execution("fix_video_format", "failure")
            traceback.print_exc()
            return

    # Step 3: Process Videos
    if config["steps"]["process_videos"]["enabled"]:
        try:
            logging.info("Step 3: Processing Videos...")
            setup_directories_and_yaml(output_path=output_path)
            from ultralytics import YOLO
            process_videos(
                videos_path=config["paths"]["downloads"],
                framerate=config["video"]["framerate"],
                output_path=output_path,
                model=YOLO(os.environ["MODEL_PATH"]),
            )
            compress_folder(folder_path=output_path, output_zip=os.path.join(output_path, "labels.zip"))
            save_last_execution("process_videos", "success")
        except Exception as e:
            logging.error(f"Error in Step 3: {e}")
            save_last_execution("process_videos", "failure")
            traceback.print_exc()
            return

    # Step 4: Upload Labels
    if config["steps"]["upload_labels"]["enabled"]:
        try:
            logging.info("Step 4: Uploading Labels...")
            upload_task(
                user=os.environ["CVAT_USER"],
                password=os.environ["CVAT_PASSWORD"],
                task_name=task_name,
                project_id=int(os.environ["CVAT_PROJECT_ID"]),
                images_dir=os.path.join(output_path, "images/train"),
                annotations_dir=os.path.join(output_path, "labels.zip"),
                annotations_format=config["cvat"]["annotations_format"],
            )
            save_last_execution("upload_labels", "success")
        except Exception as e:
            logging.error(f"Error in Step 4: {e}")
            save_last_execution("upload_labels", "failure")
            traceback.print_exc()
            return

    # Step 5: Download Labels
    if config["steps"]["download_labels"]["enabled"]:
        try:
            logging.info("Step 5: Downloading Labels...")
            download_finished_tasks(
                user=os.environ["CVAT_USER"],
                password=os.environ["CVAT_PASSWORD"],
                annotations_format=config["cvat"]["annotations_format"],
            )
            save_last_execution("download_labels", "success")
        except Exception as e:
            logging.error(f"Error in Step 5: {e}")
            save_last_execution("download_labels", "failure")
            traceback.print_exc()
            return

    # Step 6: Clean Labels
    if config["steps"]["clear_empty_labels"]["enabled"]:
        try:
            logging.info("Step 6: Cleaning Labels...")
            compare_and_remove(root_path=config["paths"]["output"])
            save_last_execution("clean_labels", "success")
        except Exception as e:
            logging.error(f"Error in Step 6: {e}")
            save_last_execution("clean_labels", "failure")
            traceback.print_exc()
            return

    logging.info("Pipeline completed successfully!")

if __name__ == "__main__":
    main()
