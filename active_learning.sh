#!/bin/bash

# Define the Python scripts to execute
scripts=(
    "scripts/download_yt_videos.py"
    "scripts/fix_video_format.py"
    "scripts/process_video.py"
)

# Define the Python interpreter to use
PYTHON="venv/bin/python3"

# Loop through the scripts and execute them
for script in "${scripts[@]}"; do
    echo "Executing $script..."
    $PYTHON "$script"
    
    # Check if the script executed successfully
    if [ $? -ne 0 ]; then
        echo "Error: $script failed to execute. Exiting."
        exit 1
    fi

done

echo "All scripts executed successfully."
