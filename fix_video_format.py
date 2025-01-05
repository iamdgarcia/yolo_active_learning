import os
import subprocess

def process_videos_in_folder(folder_path):
    """
    Processes all videos in a folder using ffmpeg to change the pixel format to yuv420p.
    Removes the original videos after processing.

    Parameters:
    - folder_path (str): Path to the folder containing the videos.
    """
    if not os.path.exists(folder_path):
        print(f"Folder {folder_path} does not exist.")
        return

    # Get a list of video files in the folder
    video_files = [f for f in os.listdir(folder_path) if f.endswith('.webm')]

    if not video_files:
        print(f"No video files found in folder {folder_path}.")
        return

    for video in video_files:
        input_path = os.path.join(folder_path, video)
        output_path = os.path.join(folder_path, f"processed_{video}")

        # Run ffmpeg command
        command = [
            "ffmpeg",
            "-i", input_path,
            "-pix_fmt", "yuv420p",
            output_path
        ]

        print(f"Processing video: {video}")
        try:
            subprocess.run(command, check=True)
            print(f"Successfully processed: {video}")

            # Remove the original file after successful processing
            os.remove(input_path)
            print(f"Removed original file: {video}")

            # Rename the processed file to the original name
            os.rename(output_path, input_path)
            print(f"Renamed processed file: {output_path} to {input_path}")
        except subprocess.CalledProcessError as e:
            print(f"Error processing {video}: {e}")
            if os.path.exists(output_path):
                os.remove(output_path)  # Cleanup partially processed file

if __name__ == "__main__":
    folder_path = "downloads"
    process_videos_in_folder(folder_path)
