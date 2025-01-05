import os
import yt_dlp
import json

def load_downloaded_videos(file_path="data/downloaded_videos.json"):
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return json.load(file)
    return []

def save_downloaded_videos(downloaded_videos, file_path="data/downloaded_videos.json"):
    with open(file_path, "w") as file:
        json.dump(downloaded_videos, file, indent=4)

def search_and_download_videos(query, num_results, resolution, download_path, log_file="data/downloaded_videos.json"):
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    downloaded_videos = load_downloaded_videos(log_file)

    ydl_opts = {
        "format": f"bestvideo[height<={resolution}]+bestaudio/best",
        "outtmpl": f"{download_path}/%(title)s.%(ext)s",
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        downloaded_count = 0
        page = 1

        while downloaded_count < num_results:
            search_results = ydl.extract_info(f"ytsearch{num_results * page}:{query}", download=False)["entries"]
            if not search_results:
                print(f"No more results for query: {query}")
                break

            for video in search_results:
                if downloaded_count >= num_results:
                    break

                video_id = video["id"]
                video_title = video["title"]
                video_url = video["webpage_url"]

                if any(v["id"] == video_id for v in downloaded_videos):
                    print(f"Skipping already downloaded video: {video_title}")
                    continue

                print(f"Downloading video: {video_title}")
                try:
                    ydl.download([video_url])
                    downloaded_videos.append({"id": video_id, "title": video_title, "url": video_url})
                    save_downloaded_videos(downloaded_videos, log_file)
                    downloaded_count += 1
                except Exception as e:
                    print(f"Error downloading {video_title}: {e}")
            page += 1
