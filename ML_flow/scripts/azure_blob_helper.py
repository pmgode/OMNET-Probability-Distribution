import os
import sys
from azure.storage.blob import ContainerClient
from dotenv import load_dotenv
from loguru import logger


def init_container_client(container_name):
    """
    Return a client for Azure Blob Storage with given CONTAINER_NAME.
    """
    # Load secret connection string from environment
    load_dotenv()
    try:
        CONNECTION_STRING = os.environ["AZURE_STORAGE_CONNECTION_STRING"]
    except KeyError:
        logger.error("AZURE_STORAGE_CONNECTION_STRING not found in environment.")
        sys.exit(1)
    # Connect to container
    try:
        container_client = ContainerClient.from_connection_string(
            CONNECTION_STRING, container_name
        )
        logger.info(
            f"Successfully connected to Azure Blob Container '{container_name}'."
        )
    except Exception as e:
        logger.error(
            f"Failed to connect to Azure Blob Container '{container_name}':{e}"
        )
        exit(1)
    return container_client


def download_blob(container_client, blob_name, dest, when_missing):
    """
    Download a blob with given BLOB_NAME from CONTAINER_CLIENT to DEST.
    If DEST is a directory, the blob will be downloaded as BLOB_NAME under DEST.
    If WHEN_MISSING is true, only download files that don't exist yet.
    Returns the path of the downloaded file.
    """
    # Build final path
    dest = os.path.join(dest, blob_name) if os.path.isdir(dest) else dest
    dest = os.path.abspath(dest)
    print(dest)
    # Handle when_missing option
    if when_missing:
        if os.path.isfile(dest):
            logger.info(
                f"File at download destination '{dest}' already exists. Skipping!"
            )
            return dest

    # Connect to blob
    try:
        blob_client = container_client.get_blob_client(blob_name)
        logger.info(f"Starting download of blob '{blob_name}'.")
    except Exception as e:
        logger.error(f"Failed to connect to blob client: {e}")

    # Download blob
    with open(dest, "wb") as file:
        stream = blob_client.download_blob()
        for chunk in stream.chunks():
            file.write(chunk)
    return dest


def list_blobs_in_container(container_client):
    """
    Return a list of all blobs in CONTAINER_CLIENT.
    """
    try:
        # Get a client to interact with the specified container
        # List all blobs in the container
        blobs = container_client.list_blobs()
        return [blob.name for blob in blobs]
    except Exception as e:
        logger.error(
            f"Failed to list blobs in the container {container_client.name}: {e}"
        )
        return []
