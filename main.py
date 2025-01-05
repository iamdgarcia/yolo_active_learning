import logging
import os
import traceback
from dotenv import load_dotenv
from modules.downloader import search_and_download_videos
from modules.formatter import fix_video_format
from modules.processor import process_videos, setup_directories_and_yaml, compress_folder
from modules.uploader import upload_task
from modules.label_manager import compare_and_remove, download_finished_tasks
from modules.utils import load_config, load_last_execution, save_last_execution, get_task_name

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("pipeline.log"),
    ],
)

def main():
    # Load configuration and environment variables
    try:
        load_dotenv()
        config = load_config("data/config.yaml")
        last_execution = load_last_execution()

        # Determine task name and output path
        task_name = get_task_name(config["cvat"]["task_name"])
        output_path = f"{config['paths']['output']}/{task_name}"

        logging.info(f"Last Execution: {last_execution}")
        logging.info(f"Task Name: {task_name}")
    except Exception as e:
        logging.error(f"Failed to load configuration or execution data: {e}")
        traceback.print_exc()
        return

    # Step 1: Download YouTube Videos
    if config["steps"]["download_videos"]["enabled"]:
        try:
            logging.info("Step 1: Downloading YouTube Videos...")
            search_and_download_videos(
                query=config["youtube"]["queries"],
                num_results=config["youtube"]["num_videos"],
                resolution=config["youtube"]["resolution"],
                download_path=config["paths"]["downloads"],
            )
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
            fix_video_format(folder_path=config["paths"]["downloads"])
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
            process_videos(
                videos_path=config["paths"]["downloads"],
                output_path=output_path,
                model_path=os.environ["MODEL_PATH"],
                framerate=config["video"]["framerate"],
            )
            compress_folder(folder_path=output_path, output_zip=f"{output_path}/labels.zip")
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
                images_dir=f"{output_path}/images/train",
                annotations_dir=f"{output_path}/labels.zip",
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
            compare_and_remove(root_path=output_path)
            save_last_execution("clear_empty_labels", "success")
        except Exception as e:
            logging.error(f"Error in Step 6: {e}")
            save_last_execution("clear_empty_labels", "failure")
            traceback.print_exc()
            return

    logging.info("Pipeline completed successfully!")

if __name__ == "__main__":
    main()
