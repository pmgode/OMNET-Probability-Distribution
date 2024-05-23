import os
import re
import azure_blob_helper as abh
import cv2
from cv2_object_selector import Cv2ObjectGUI
import mlflow
import mlflow.sklearn
from dotenv import load_dotenv  # Import the dotenv module

# Load environment variables from .env file
load_dotenv()

def better_blobname(blob_name):
    nums = re.findall(r'\d+', blob_name)
    date, time, rec_nr = nums[0], nums[1], nums[2]
    return f"{date}-{time}_meeting-recording-{rec_nr}"

def main(video_dir, output_dir):
    container_client = abh.init_container_client("visioncontrolvideos")

    # Create folders if missing
    if not os.path.exists(video_dir):
        os.makedirs(video_dir)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Start MLflow experiment
    mlflow.set_experiment("Anomaly Detection Video Processing")

    with mlflow.start_run() as run:
        # Log parameters
        mlflow.log_param("video_dir", video_dir)
        mlflow.log_param("output_dir", output_dir)

        # Download video if missing and open GUI for object selection
        for num, blob in enumerate(abh.list_blobs_in_container(container_client)):
            blob_name = better_blobname(blob)
            dest = os.path.join(video_dir, blob_name)

            # Log the blob name being processed
            mlflow.log_param(f"blob_{num}", blob_name)

            # Download video if not already available
            vid = abh.download_blob(
                container_client=container_client,
                blob_name=blob,
                dest=dest,
                when_missing=True,
            )

            # Start Object Selection GUI
            obj_selector = Cv2ObjectGUI(
                window_name=blob_name,
                cap=cv2.VideoCapture(vid),
                output_dir=output_dir,
                output_prefix=blob_name,
            )
            obj_selector.play()
            obj_selector.set_to_second(10)
            obj_selector.quit()

            # Log output files
            output_files = [f for f in os.listdir(output_dir) if f.startswith(blob_name)]
            for output_file in output_files:
                mlflow.log_artifact(os.path.join(output_dir, output_file))

if __name__ == "__main__":
    video_dir = "./Prerecordings"
    output_dir = "./output"
    main(video_dir, output_dir)
