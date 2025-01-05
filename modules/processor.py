from ultralytics import YOLO
import os
import cv2
import datetime
import zipfile

def compress_folder(folder_path, output_zip):
    """
    Compress the contents of a folder into a ZIP file.

    Args:
        folder_path (str): Path to the folder to be compressed.
        output_zip (str): Path to the output ZIP file.
    """
    # Ensure the folder exists
    if not os.path.isdir(folder_path):
        raise ValueError(f"The folder '{folder_path}' does not exist.")

    # Create a ZIP file
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Walk through the directory
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                # Get the full file path
                file_path = os.path.join(root, file)
                # Get the relative path to preserve folder structure
                arcname = os.path.relpath(file_path, start=folder_path)
                # Add file to the ZIP archive
                zipf.write(file_path, arcname=arcname)

    print(f"Folder '{folder_path}' compressed successfully into '{output_zip}'.")


def setup_directories_and_yaml(output_path):
    """
    Sets up the directory structure and creates a YAML configuration file.

    Args:
        output_path (str): The base directory where the structure and YAML file will be created.
    """
    # Ensure the output path exists
    if not os.path.exists(output_path):
        os.makedirs(output_path, exist_ok=True)
        print(f"Output directory created: {output_path}")

    # Define the directory structure
    directories = [
        os.path.join(output_path, "images"),
        os.path.join(output_path, "images/train"),
        os.path.join(output_path, "labels"),
        os.path.join(output_path, "labels/train")
    ]
    
    # Create each directory if it doesn't exist
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Directory created: {directory}")

    # Define the YAML content
    yaml_content = """names:
  0: corner
  1: area_fondo
  2: esquina_area
  3: penalti_fondo
  4: esquina_penalti
  5: area_circ
  6: centro_banda
  7: centro_circ
  8: centro
  9: penalti
  10: goal_down
  11: goal_up
path: .
train: Train.txt
"""
    # Write the YAML file
    yaml_path = os.path.join(output_path, "data.yaml")
    with open(yaml_path, "w") as yaml_file:
        yaml_file.write(yaml_content)
        print(f"YAML file created: {yaml_path}")
def process_videos(videos_path, output_path, model_path, framerate=180):
    model = YOLO(model_path)
    setup_directories_and_yaml(output_path)

    for video in os.listdir(videos_path):
        video_path = os.path.join(videos_path, video)
        cap = cv2.VideoCapture(video_path)

        i, ret = 0, True
        while ret:
            i += 1
            ret, frame = cap.read()

            if not ret or i % framerate != 0:
                continue

            frame_path = os.path.join(output_path, f"images/train/frame_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{i}.jpg")
            results = model.predict(frame, verbose=False)
            cv2.imwrite(frame_path, frame)
