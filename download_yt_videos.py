import yt_dlp
import os
import json

def load_downloaded_videos(file_path="downloaded_videos.json"):
    """Load the log of downloaded videos."""
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return json.load(file)
    return []

def save_downloaded_videos(downloaded_videos, file_path="downloaded_videos.json"):
    """Save the log of downloaded videos."""
    with open(file_path, "w") as file:
        json.dump(downloaded_videos, file, indent=4)

def search_and_download_yt_dlp(query, num_results=1, resolution='best', download_path="downloads", log_file="downloaded_videos.json"):
    """
    Search YouTube and download videos using yt-dlp with a specific resolution, avoiding duplicates.

    Parameters:
    - query (str): The search query.
    - num_results (int): Number of new videos to download.
    - resolution (str): Resolution of the video to download (e.g., '1080p', '720p', '480p', 'best').
    - download_path (str): Path to save the downloaded videos.
    - log_file (str): Path to the log file for downloaded videos.
    """
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    # Load the log of downloaded videos
    downloaded_videos = load_downloaded_videos(log_file)

    # Configure yt-dlp
    ydl_opts = {
        "format": f"bestvideo[height<={resolution}]+bestaudio/best",
        "outtmpl": f"{download_path}/%(title)s.%(ext)s",
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        downloaded_count = 0
        page = 1  # yt-dlp will use pagination for searches beyond `num_results`

        while downloaded_count < num_results:
            # Perform search with pagination
            search_results = ydl.extract_info(f"ytsearch{num_results * page}:{query}", download=False)["entries"]
            if not search_results:
                print(f"No more results found for query: {query}")
                break

            for video in search_results:
                if downloaded_count >= num_results:
                    break

                video_id = video["id"]
                video_title = video["title"]
                video_url = video["webpage_url"]

                # Check if video is already downloaded
                if any(v["id"] == video_id for v in downloaded_videos):
                    print(f"Skipping already downloaded video: {video_title}")
                    continue

                # Download the video
                print(f"Downloading video: {video_title} ({video_url})")
                try:
                    ydl.download([video_url])
                    # Log the downloaded video
                    downloaded_videos.append({"id": video_id, "title": video_title, "url": video_url})
                    save_downloaded_videos(downloaded_videos, log_file)
                    downloaded_count += 1
                except Exception as e:
                    print(f"Failed to download video: {video_title}. Error: {e}")

            page += 1  # Increment the search pagination for more results

        print(f"Downloaded {downloaded_count} new videos.")

if __name__ == "__main__":
    import numpy as np
    querys = ["Resumen la liga EA", "resumen Serie A", "Resumen Bundesliga","resumen liga hypermotion","resumen premier league","resumen MLS"]
    num_videos = 1
    resolutions = ["best","720","1080"]
    for q in querys:
        r = np.random.choice(resolutions)
        print(r)
        # If the user inputs "best", no need to set a resolution limit
        resolution = r if r != "best" else ""

        search_and_download_yt_dlp(q, num_videos, resolution)
