import yt_dlp
import os

def search_and_download_yt_dlp(query, num_results=1, resolution='best', download_path="downloads"):
    """
    Search YouTube and download videos using yt-dlp with a specific resolution.

    Parameters:
    - query (str): The search query.
    - num_results (int): Number of videos to download.
    - resolution (str): Resolution of the video to download (e.g., '1080p', '720p', '480p', 'best').
    - download_path (str): Path to save the downloaded videos.
    """
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    # Configure yt-dlp
    ydl_opts = {
        "format": f"bestvideo[height<={resolution}]+bestaudio/best",
        "outtmpl": f"{download_path}/%(title)s.%(ext)s",
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # Perform search
        search_results = ydl.extract_info(f"ytsearch{num_results}:{query}", download=False)["entries"]
        if not search_results:
            print(f"No results found for query: {query}")
            return
        # Download videos
        for i, video in enumerate(search_results, start=1):
            print(f"Downloading video {i}/{num_results}: {video['title']} ({video['webpage_url']})")
            ydl.download([video["webpage_url"]])

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
