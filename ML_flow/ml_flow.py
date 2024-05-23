import os
import cv2
import numpy as np
from loguru import logger
from sklearn.ensemble import IsolationForest
import mlflow
import mlflow.sklearn

def convert_to_grayscale(image):
    """
    Converts a color image to grayscale.
    Parameters:
        image: numpy array representing the input color image.
    Returns:
        numpy array: Grayscale version of the input image.
    """
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return gray_image

def get_image_paths(folder):
    """
    Get paths to all image files in a folder.
    Parameters:
        folder: Path to the folder containing images.
    Returns:
        list: List of paths to image files.
    """
    image_paths = []
    if not os.path.exists(folder):
        logger.error(f"Folder {folder} does not exist")
    for filename in os.listdir(folder):
        img_path = os.path.join(folder, filename)
        if os.path.isfile(img_path):
            image_paths.append(img_path)
    return image_paths

def load_images(image_paths):
    """
    Load images from given paths.
    Parameters:
        image_paths: List of paths to image files.
    Returns:
        list: List of numpy arrays representing input color images.
    """
    images = []
    for img_path in image_paths:
        image = cv2.imread(img_path)
        if image is not None:
            images.append(image)
    return images

def generate_model(images):
    """
    Generates an anomaly detection model.
    Parameters:
        images: List of numpy arrays representing input color images.
    Returns:
        sklearn.ensemble.IsolationForest: Anomaly detection model.
    """
    # Convert images to grayscale
    grayscale_images = [convert_to_grayscale(image) for image in images]

    # Flatten images for model input
    flattened_images = [image.flatten() for image in grayscale_images]

    # Train Isolation Forest model
    model = IsolationForest(random_state=42)
    model.fit(flattened_images)

    return model

def is_anomaly(image, model, threshold=0.005):
    """
    Checks if an input image is an anomaly.
    Parameters:
        image: numpy array representing the input color image.
        model: Anomaly detection model.
        threshold: Threshold for anomaly detection score.
    Returns:
        bool: True if the input image is an anomaly, False otherwise.
    """
    # Convert image to grayscale
    gray_image = convert_to_grayscale(image)

    # Flatten image for model input
    flattened_image = gray_image.flatten()

    # Predict anomaly score
    anomaly_score = model.decision_function([flattened_image])[0]

    # Check if anomaly score exceeds threshold
    return anomaly_score < threshold

def resize_if_needed(image_path, target_size):
    """
    Resizes image if its dimensions don't fit the target size.
    """
    image = cv2.imread(image_path)
    image_size = (image.shape[0], image.shape[1])
    if image_size != target_size:
        cv2.imwrite(image_path, cv2.resize(image, target_size))

# Full path to the folder containing training images
script_dir = os.path.dirname(os.path.realpath(__file__))
training_folder = os.path.join(script_dir, "data")

# Get paths to image files
training_image_paths = get_image_paths(training_folder)

# Load images from paths
training_images = load_images(training_image_paths)

# Integrate with MLflow
mlflow.set_experiment("Anomaly Detection Experiment")

with mlflow.start_run() as run:
    # Log parameters
    mlflow.log_param("threshold", 0.005)

    # Log the training data as an artifact
    train_data_file = "train_data_paths.txt"
    with open(train_data_file, "w") as f:
        for path in training_image_paths:
            f.write(f"{path}\n")
    mlflow.log_artifact(train_data_file)
    os.remove(train_data_file)

    # Generate and log model
    model = generate_model(training_images)
    mlflow.sklearn.log_model(model, "isolation_forest_model")

    # Full path to folder containing test folder
    test_folder = os.path.join(script_dir, "test-data")

    # Get paths to image files
    test_image_paths = get_image_paths(test_folder)

    # Resize all test images to shape of training images
    target_size = (training_images[0].shape[1], training_images[0].shape[0])

    for path in test_image_paths:
        resize_if_needed(path, target_size)

    # Detect anomalies and log results
    anomaly_results = []
    for path in test_image_paths:
        test_image = cv2.imread(path)
        result = is_anomaly(test_image, model)
        if result:
            logger.warning(f"{path} is an anomaly!")
            anomaly_results.append((path, "anomaly"))
        else:
            logger.info(f"{path} is not an anomaly")
            anomaly_results.append((path, "not_anomaly"))

    # Log the anomaly results as an artifact
    anomaly_results_file = "anomaly_results.txt"
    with open(anomaly_results_file, "w") as f:
        for path, result in anomaly_results:
            f.write(f"{path}: {result}\n")
    mlflow.log_artifact(anomaly_results_file)
    os.remove(anomaly_results_file)
