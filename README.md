# **Active Learning Pipeline**

This repository contains an active learning pipeline for efficiently downloading, processing, and managing datasets for object detection tasks using YOLO. The pipeline automates tasks such as video downloading, video formatting, frame extraction, label uploading, and dataset organization.

---

## **Table of Contents**
1. [Overview](#overview)
2. [Pipeline Workflow](#pipeline-workflow)
3. [Setup Instructions](#setup-instructions)
4. [Configuration](#configuration)
5. [Execution](#execution)
6. [Scheduling Periodic Executions](#scheduling-periodic-executions)
7. [Folder Structure](#folder-structure)
8. [Troubleshooting](#troubleshooting)

---

## **Overview**
The active learning pipeline automates the following:
1. Downloading raw video data from YouTube.
2. Formatting videos for compatibility with further processing.
3. Extracting frames from videos and generating labels using YOLO inference.
4. Uploading the extracted data to labeling platforms (e.g., CVAT).
5. Downloading completed labels from the labeling platform.
6. Cleaning datasets to ensure consistency.

---

## **Pipeline Workflow**
The pipeline consists of the following steps:

1. **Download Videos**: Fetch relevant videos from YouTube based on predefined queries.
2. **Fix Video Format**: Ensure downloaded videos meet the required format for further processing.
3. **Process Videos**:
   - Extract frames from videos.
   - Run YOLO inference to generate labels for object detection.
   - Save processed frames and labels in an organized structure.
4. **Upload Labels**: Send generated data to CVAT for manual refinement and validation.
5. **Download Labels**: Retrieve the manually labeled datasets from CVAT.
6. **Clean Labels**: Remove frames that lack corresponding labels to maintain dataset integrity.

---

## **Setup Instructions**

### **Prerequisites**
1. **Python**: Install Python 3.9 or later.
2. **Dependencies**: Install required libraries from `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```
3. **Environment Variables**:
   - Create a `.env` file in the root directory with the following:
     ```env
     CVAT_USER=<Your CVAT Username>
     CVAT_PASSWORD=<Your CVAT Password>
     CVAT_PROJECT_ID=<Your CVAT Project ID>
     MODEL_PATH=<Path to YOLO Model>
     ```

### **Folder Structure**
- **`data/`**: Contains configurations, logs, and datasets.
- **`modules/`**: Contains modular Python scripts for each step in the pipeline.
- **`pipeline.log`**: Stores execution logs.

---

## **Configuration**
The pipeline is configured via `data/config.yaml`. Update the configuration as needed:

```yaml
paths:
  downloads: "downloads"          # Directory to save downloaded videos
  output: "assets/frames"         # Directory to save processed data

youtube:
  queries:
    - "Resumen la liga EA"
    - "Resumen Serie A"
    - "Resumen Bundesliga"
  num_videos: 3                   # Number of videos to download per query
  resolution: "720"               # Video resolution

video:
  framerate: 180                  # Extract one frame every 3 minutes

cvat:
  task_name: "auto"               # Task name ("auto" generates name based on date)
  annotations_format: "YOLOv8 Detection 1.0"

steps:
  download_videos:
    enabled: true
  fix_video_format:
    enabled: true
  process_videos:
    enabled: true
  upload_labels:
    enabled: true
  download_labels:
    enabled: true
  clear_empty_labels:
    enabled: true
```

---

## **Execution**
Run the pipeline using the `main.py` script:

```bash
python main.py
```

### **Step-by-Step Breakdown**
1. **Downloading Videos**:
   - Downloads videos using YouTube queries from the configuration.
   - Tracks downloaded videos to avoid duplicates.

2. **Fixing Video Format**:
   - Converts videos to the required pixel format (`yuv420p`).

3. **Processing Videos**:
   - Extracts frames at regular intervals.
   - Uses YOLO for initial object detection and label generation.
   - Saves frames and labels in the `output` directory.

4. **Uploading Labels**:
   - Uploads the generated frames and labels to CVAT.

5. **Downloading Labels**:
   - Retrieves validated labels from CVAT for further processing.

6. **Cleaning Labels**:
   - Ensures only frames with valid labels are retained.

---

## **Scheduling Periodic Executions**
To run the pipeline periodically, use a scheduler like **cron** or **GitHub Actions**.

### **1. Using Cron (Linux/MacOS)**
1. Open the cron editor:
   ```bash
   crontab -e
   ```
2. Add an entry to run the pipeline daily at midnight:
   ```bash
   0 0 * * * /usr/bin/python3 /path/to/main.py >> /path/to/pipeline.log 2>&1
   ```

### **2. Using GitHub Actions**
1. Create `.github/workflows/pipeline.yml`:
   ```yaml
   name: Active Learning Pipeline

   on:
     schedule:
       - cron: "0 0 * * *"  # Run daily at midnight (UTC)
     workflow_dispatch:  # Manual execution

   jobs:
     pipeline:
       runs-on: ubuntu-latest
       steps:
         - name: Checkout repository
           uses: actions/checkout@v4

         - name: Set up Python
           uses: actions/setup-python@v4
           with:
             python-version: '3.9'

         - name: Install dependencies
           run: |
             pip install -r requirements.txt

         - name: Run Pipeline
           env:
             CVAT_USER: ${{ secrets.CVAT_USER }}
             CVAT_PASSWORD: ${{ secrets.CVAT_PASSWORD }}
             CVAT_PROJECT_ID: ${{ secrets.CVAT_PROJECT_ID }}
             MODEL_PATH: ${{ secrets.MODEL_PATH }}
           run: |
             python main.py
   ```

2. Add your secrets in the repository settings under `Settings > Secrets and variables > Actions`.

---

## **Troubleshooting**
### **Common Issues**
1. **Missing Dependencies**:
   - Ensure all dependencies are installed using `pip install -r requirements.txt`.

2. **Invalid Configuration**:
   - Verify `config.yaml` and `.env` for correctness.

3. **Access Issues in CVAT**:
   - Check if your CVAT credentials and project ID are valid.

### **Logs**
Refer to `pipeline.log` for detailed error messages and execution details.