"""Google Drive API utilities."""

import logging
import os
from pathlib import Path
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

# Scopes required for uploading files to Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive.file']


def authenticate(credentials_path: Path):
    """
    Authenticate with Google Drive API.
    
    Args:
        credentials_path: Path to the OAuth2 credentials JSON file
        
    Returns:
        Google Drive API service object
        
    Raises:
        RuntimeError: If authentication fails
    """
    creds = None
    token_path = Path("token.json")
    
    # The token.json stores the user's access and refresh tokens
    if token_path.exists():
        logger.debug("Loading existing token")
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.debug("Refreshing expired token")
            try:
                creds.refresh(Request())
            except Exception as e:
                logger.warning(f"Token refresh failed: {e}. Re-authenticating...")
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
            flow = InstalledAppFlow.from_client_secrets_file(
                str(credentials_path), SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        logger.debug("Saving token for future use")
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    
    try:
        service = build('drive', 'v3', credentials=creds)
        logger.debug("Successfully authenticated with Google Drive")
        return service
    except Exception as e:
        raise RuntimeError(f"Failed to build Google Drive service: {e}")


def find_or_create_folder(service, folder_name: str, parent_id: Optional[str] = None) -> str:
    """
    Find a folder by name or create it if it doesn't exist.
    
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
        
        results = service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)'
        ).execute()
        
        items = results.get('files', [])
        
        if items:
            logger.debug(f"Found existing folder: {folder_name} (ID: {items[0]['id']})")
            return items[0]['id']
        
        # Create new folder
        logger.debug(f"Creating new folder: {folder_name}")
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id:
            file_metadata['parents'] = [parent_id]
        
        folder = service.files().create(
            body=file_metadata,
            fields='id'
        ).execute()
        
        logger.debug(f"Created folder with ID: {folder['id']}")
        return folder['id']
        
    except HttpError as e:
        raise RuntimeError(f"Failed to find or create folder: {e}")


def upload_file(service, file_path: Path, destination: str) -> str:
    """
    Upload a file to Google Drive.
    
    Args:
        service: Google Drive API service object
        file_path: Path to the file to upload
        destination: Destination folder name or ID
        
    Returns:
        URL to view the uploaded file
        
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
        file_metadata = {
            'name': file_path.name,
            'parents': [folder_id]
        }
        
        media = MediaFileUpload(
            str(file_path),
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            resumable=True
        )
        
        logger.debug(f"Uploading {file_path.name}...")
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()
        
        file_id = file.get('id')
        web_view_link = file.get('webViewLink')
        
        logger.debug(f"Uploaded file ID: {file_id}")
        
        return web_view_link
        
    except HttpError as e:
        raise RuntimeError(f"Failed to upload file: {e}")
    except Exception as e:
        raise RuntimeError(f"Upload error: {e}")
