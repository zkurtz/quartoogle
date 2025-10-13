"""Google Drive API utilities."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

logger = logging.getLogger(__name__)


def find_or_create_folder(service: Any, folder_name: str, parent_id: Optional[str] = None) -> str:
    """Find a folder by name or create it if it doesn't exist.

    Args:
        service: Google Drive API service object
        folder_name: Name of the folder to find or create
        parent_id: Optional parent folder ID

    Returns:
        Folder ID
    """
    try:
        # Search for existing folder
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        if parent_id:
            query += f" and '{parent_id}' in parents"

        results = service.files().list(q=query, spaces="drive", fields="files(id, name)").execute()

        items = results.get("files", [])

        if items:
            logger.debug(f"Found existing folder: {folder_name} (ID: {items[0]['id']})")
            return items[0]["id"]

        # Create new folder
        logger.debug(f"Creating new folder: {folder_name}")
        file_metadata: dict[str, Any] = {"name": folder_name, "mimeType": "application/vnd.google-apps.folder"}
        if parent_id:
            file_metadata["parents"] = [parent_id]

        folder = service.files().create(body=file_metadata, fields="id").execute()

        logger.debug(f"Created folder with ID: {folder['id']}")
        return folder["id"]

    except HttpError as e:
        raise RuntimeError(f"Failed to find or create folder: {e}")


def upload_file(service: Any, file_path: Path, destination: str) -> tuple[str, str]:
    """Upload a file to Google Drive with a timestamp suffix.

    The file will be uploaded with a timestamp appended to the filename in the format:
    [basename]_YYYY-MM-DD_HH-MM[extension], e.g., "report_2025-10-13_08-01.docx".
    The timestamp is in the local time zone of the system executing the upload.

    Args:
        service: Google Drive API service object
        file_path: Path to the file to upload
        destination: Destination folder name or ID

    Returns:
        Tuple of (file_id, web_view_link) for the uploaded file

    Raises:
        RuntimeError: If upload fails
    """
    try:
        # Determine if destination is an ID or name
        # IDs are typically long alphanumeric strings
        if len(destination) > 20 and destination.isalnum():
            folder_id = destination
            logger.debug(f"Using destination as folder ID: {folder_id}")
        else:
            # Treat as folder name, find or create it
            folder_id = find_or_create_folder(service, destination)

        # Upload the file with timestamp suffix
        # Generate timestamp in format: YYYY-MM-DD_HH-MM
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")

        # Add timestamp before file extension
        file_stem = file_path.stem  # filename without extension
        file_suffix = file_path.suffix  # extension with dot
        timestamped_name = f"{file_stem}_{timestamp}{file_suffix}"

        file_metadata: dict[str, Any] = {"name": timestamped_name, "parents": [folder_id]}

        media = MediaFileUpload(
            str(file_path),
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            resumable=True,
        )

        logger.debug(f"Uploading {file_path.name} as {timestamped_name}...")
        file = service.files().create(body=file_metadata, media_body=media, fields="id, webViewLink").execute()

        file_id = file.get("id")
        web_view_link = file.get("webViewLink")

        logger.debug(f"Uploaded file ID: {file_id}")

        return file_id, web_view_link

    except HttpError as e:
        raise RuntimeError(f"Failed to upload file: {e}")
    except Exception as e:
        raise RuntimeError(f"Upload error: {e}")
