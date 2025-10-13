"""Google Drive API utilities."""

import logging
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
    """Upload a file to Google Drive.

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

        # Upload the file
        file_metadata: dict[str, Any] = {"name": file_path.name, "parents": [folder_id]}

        media = MediaFileUpload(
            str(file_path),
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            resumable=True,
        )

        logger.debug(f"Uploading {file_path.name}...")
        file = service.files().create(body=file_metadata, media_body=media, fields="id, webViewLink").execute()

        file_id = file.get("id")
        web_view_link = file.get("webViewLink")

        logger.debug(f"Uploaded file ID: {file_id}")

        return file_id, web_view_link

    except HttpError as e:
        raise RuntimeError(f"Failed to upload file: {e}")
    except Exception as e:
        raise RuntimeError(f"Upload error: {e}")


def set_pageless_format(docs_service: Any, file_id: str) -> None:
    """Set the document to pageless format.

    Args:
        docs_service: Google Docs API service object
        file_id: ID of the document to format

    Raises:
        RuntimeError: If formatting fails
    """
    try:
        logger.debug(f"Setting document {file_id} to pageless format...")

        # Get the current document to check if it exists
        docs_service.documents().get(documentId=file_id).execute()

        # Update document style to use pageless format
        # Pageless format in Google Docs is achieved by setting useCustomHeaderFooterMargins to False
        # and not specifying page size, which allows content to flow continuously
        requests = [
            {
                "updateDocumentStyle": {
                    "documentStyle": {
                        "useCustomHeaderFooterMargins": False,
                        "marginTop": {"magnitude": 72, "unit": "PT"},
                        "marginBottom": {"magnitude": 72, "unit": "PT"},
                        "marginLeft": {"magnitude": 72, "unit": "PT"},
                        "marginRight": {"magnitude": 72, "unit": "PT"},
                    },
                    "fields": "useCustomHeaderFooterMargins,marginTop,marginBottom,marginLeft,marginRight",
                }
            }
        ]

        docs_service.documents().batchUpdate(documentId=file_id, body={"requests": requests}).execute()

        logger.debug("Successfully set document to pageless format")

    except Exception as e:
        # Log warning but don't fail the upload
        logger.warning(f"Failed to set pageless format (document still uploaded successfully): {e}")
