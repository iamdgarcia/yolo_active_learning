import os
import subprocess

def fix_video_format(folder_path, pixel_format="yuv420p"):
    if not os.path.exists(folder_path):
        print(f"Folder {folder_path} does not exist.")
        return

    video_files = [f for f in os.listdir(folder_path) if f.endswith('.webm')]

    for video in video_files:
        input_path = os.path.join(folder_path, video)
        output_path = os.path.join(folder_path, f"processed_{video}")

        command = ["ffmpeg", "-i", input_path, "-pix_fmt", pixel_format, output_path]

        try:
            subprocess.run(command, check=True)
            os.remove(input_path)
            os.rename(output_path, input_path)
            print(f"Processed and fixed video: {input_path}")
        except subprocess.CalledProcessError as e:
            print(f"Error processing video {input_path}: {e}")
