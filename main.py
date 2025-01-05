import logging
import os
import traceback
from dotenv import load_dotenv
from download_yt_videos import search_and_download_yt_dlp
from fix_video_format import process_videos_in_folder
from process_video import setup_directories_and_yaml, process_videos, compress_folder
from download_labels import download_finished_tasks
from clear_empty_labels import compare_and_remove
from upload_labels import upload_task
import yaml



def load_config(config_path="config.yaml"):
    """Load configuration from a YAML file."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    with open(config_path, "r") as file:
        return yaml.safe_load(file)

def main():
    # Load environment variables and configuration
    try:
        load_dotenv()
        config = load_config("config.yaml")
    except Exception as e:
        logging.error(f"Failed to load configuration: {e}")
        traceback.print_exc()
        return

    try:
        # Step 1: Download YouTube Videos
        logging.info("Step 1: Downloading YouTube Videos...")
        queries = config["youtube"]["queries"]
        num_videos = config["youtube"]["num_videos"]
        resolution = config["youtube"]["resolution"]
        search_and_download_yt_dlp(queries, num_results=num_videos, resolution=resolution)
    except Exception as e:
        logging.error(f"Error in Step 1: {e}")
        traceback.print_exc()
        return

    try:
        # Step 2: Fix Video Format
        logging.info("Step 2: Fixing Video Format...")
        process_videos_in_folder(folder_path=config["paths"]["downloads"])
    except Exception as e:
        logging.error(f"Error in Step 2: {e}")
        traceback.print_exc()
        return

    try:
        # Step 3: Process Videos
        logging.info("Step 3: Processing Videos...")
        output_path = config["paths"]["output"]
        setup_directories_and_yaml(output_path=output_path)
        process_videos(
            videos_path=config["paths"]["downloads"],
            framerate=config["video"]["framerate"],
            output_path=output_path,
            model=os.environ["MODEL_PATH"],
        )
        compress_folder(folder_path=output_path, output_zip=os.path.join(output_path, "labels.zip"))
    except Exception as e:
        logging.error(f"Error in Step 3: {e}")
        traceback.print_exc()
        return

    try:
        # Step 4: Download Labels
        logging.info("Step 4: Downloading Labels...")
        download_finished_tasks(
            user=os.environ["CVAT_USER"],
            password=os.environ["CVAT_PASSWORD"],
            task_name=config["cvat"]["task_name"],
            project_id=int(os.environ["CVAT_PROJECT_ID"]),
            images_dir=os.path.join(output_path, "images/train"),
            annotations_dir=os.path.join(output_path, "labels.zip"),
            annotations_format=config["cvat"]["annotations_format"],
        )
    except Exception as e:
        logging.error(f"Error in Step 4: {e}")
        traceback.print_exc()
        return

    try:
        # Step 5: Clear Empty Labels
        logging.info("Step 5: Clearing Empty Labels...")
        compare_and_remove(root_path=output_path)
    except Exception as e:
        logging.error(f"Error in Step 5: {e}")
        traceback.print_exc()
        return

    try:
        # Step 6: Upload Labels
        logging.info("Step 6: Uploading Labels...")
        upload_task(
            user=os.environ["CVAT_USER"],
            password=os.environ["CVAT_PASSWORD"],
            task_name=config["cvat"]["task_name"],
            project_id=int(os.environ["CVAT_PROJECT_ID"]),
            images_dir=os.path.join(output_path, "images/train"),
            annotations_dir=os.path.join(output_path, "labels.zip"),
            annotations_format=config["cvat"]["annotations_format"],
        )
        logging.info("Labels uploaded successfully.")
    except Exception as e:
        logging.error(f"Error in Step 6: {e}")
        traceback.print_exc()
        return

    logging.info("Pipeline completed successfully!")

if __name__ == "__main__":
    main()
