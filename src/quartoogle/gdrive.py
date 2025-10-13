"""Google Drive API utilities."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from google.auth.credentials import Credentials
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials as OAuth2Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

logger = logging.getLogger(__name__)

# Scopes required for uploading files to Google Drive
SCOPES = [
    "https://www.googleapis.com/auth/drive",
]


def get_drive_service(credentials_path: Path) -> Any:
    """Get Google Drive API service.

    Args:
        credentials_path: Path to the OAuth2 credentials JSON file

    Returns:
        Google Drive API v3 service object

    Raises:
        RuntimeError: If authentication or service creation fails
    """
    creds: Credentials | None = None
    token_path = credentials_path.parent / "token.json"

    # The token.json stores the user's access and refresh tokens
    if token_path.exists():
        logger.debug("Loading existing token")
        creds = OAuth2Credentials.from_authorized_user_file(str(token_path), SCOPES)

    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.debug("Refreshing expired token")
            try:
                creds.refresh(Request())
            except Exception as err:
                logger.warning(f"Token refresh failed: {err}. Re-authenticating...")
                creds = None

        if not creds:
            if not credentials_path.exists():
                raise RuntimeError(
                    f"Credentials file not found: {credentials_path}\n"
                    "Please download OAuth2 credentials from Google Cloud Console:\n"
                    "1. Go to https://console.cloud.google.com/\n"
                    "2. Create a project or select an existing one\n"
                    "3. Enable the Google Drive API\n"
                    "4. Create OAuth2 credentials (Desktop app)\n"
                    "5. Download the credentials JSON file"
                )

            logger.info("Opening browser for authentication...")
            flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        logger.debug("Saving token for future use")
        token_path.write_text(creds.to_json())

    try:
        service = build("drive", "v3", credentials=creds)
        logger.debug("Successfully authenticated with Google Drive")
        return service
    except Exception as e:
        raise RuntimeError(f"Failed to build Google Drive service: {e}")


def find_or_create_folder(service: Any, folder_name: str, parent_id: str | None = None) -> str:
    """Find a folder by name or create it if it doesn't exist.

    Args:
        service: Google Drive API service object
        folder_name: Name of the folder to find or create
        parent_id: Optional parent folder ID (None if root level)

    Returns:
        Folder ID
    """
    try:
        # Search for existing folder
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        if parent_id:
            query += f" and '{parent_id}' in parents"

        results = (
            service.files()
            .list(
                q=query,
                spaces="drive",
                fields="files(id, name)",
                supportsAllDrives=True,  # ADD THIS
                includeItemsFromAllDrives=True,  # ADD THIS
            )
            .execute()
        )

        items = results.get("files", [])

        if items:
            logger.debug(f"Found existing folder: {folder_name} (ID: {items[0]['id']})")
            return items[0]["id"]

        # Create new folder
        logger.debug(f"Creating new folder: {folder_name}")
        file_metadata: dict[str, Any] = {"name": folder_name, "mimeType": "application/vnd.google-apps.folder"}
        if parent_id:
            file_metadata["parents"] = [parent_id]

        folder = (
            service.files()
            .create(
                body=file_metadata,
                fields="id",
                supportsAllDrives=True,  # ADD THIS
            )
            .execute()
        )

        logger.debug(f"Created folder with ID: {folder['id']}")
        return folder["id"]

    except HttpError as e:
        raise RuntimeError(f"Failed to find or create folder: {e}")


def upload_file(service: Any, file_path: Path, folder_id: str) -> tuple[str, str]:
    """Upload a file to Google Drive with a timestamp suffix.

    The file will be uploaded with a timestamp appended to the filename in the format:
    [basename]_YYYY-MM-DD_HH-MM[extension], e.g., "report_2025-10-13_08-01.docx".
    The timestamp is in the local time zone of the system executing the upload.

    Args:
        service: Google Drive API service object
        file_path: Path to the file to upload
        folder_id: Google Drive folder ID (not name) where the file will be uploaded

    Returns:
        Tuple of (file_id, web_view_link) for the uploaded file

    Raises:
        RuntimeError: If upload fails
    """
    try:
        # Use the provided folder_id directly
        logger.debug(f"Using folder ID: {folder_id}")

        # Upload the file with timestamp suffix
        # Generate timestamp in format: YYYY-MM-DD_HH-MM
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")

        # Add timestamp before file extension
        file_stem = file_path.stem  # filename without extension
        file_suffix = file_path.suffix  # extension with dot
        timestamped_name = f"{file_stem}_{timestamp}{file_suffix}"

        file_metadata: dict[str, Any] = {"name": timestamped_name, "parents": [folder_id]}

        # Determine MIME type based on file extension
        mime_types = {
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".pdf": "application/pdf",
            ".html": "text/html",
            ".htm": "text/html",
        }
        mime_type = mime_types.get(file_path.suffix.lower(), "application/octet-stream")

        media = MediaFileUpload(
            str(file_path),
            mimetype=mime_type,
            resumable=True,
        )

        logger.debug(f"Uploading {file_path.name} as {timestamped_name}...")
        file = (
            service.files()
            .create(
                body=file_metadata,
                media_body=media,
                fields="id, webViewLink",
                supportsAllDrives=True,  # ADD THIS
            )
            .execute()
        )

        file_id = file.get("id")
        web_view_link = file.get("webViewLink")

        logger.debug(f"Uploaded file ID: {file_id}")

        return file_id, web_view_link

    except HttpError as e:
        raise RuntimeError(f"Failed to upload file: {e}")
    except Exception as e:
        raise RuntimeError(f"Upload error: {e}")
