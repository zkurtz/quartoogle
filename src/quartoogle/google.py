"""Google API services management."""

import logging
from functools import cached_property
from pathlib import Path
from typing import Any

import attrs
from google.auth.credentials import Credentials
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials as OAuth2Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

# Scopes required for uploading files to Google Drive and modifying documents
SCOPES = [
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/documents",
]


@attrs.frozen
class Services:
    """Google API services container.

    This class manages authentication and provides access to Google Drive and Docs API services.
    Services are created lazily using cached_property to avoid unnecessary API calls.

    Attributes:
        credentials_path: Path to the OAuth2 credentials JSON file
    """

    credentials_path: Path

    @cached_property
    def _credentials(self) -> Credentials:
        """Get or create credentials for Google APIs.

        Returns:
            Credentials object for authenticating with Google APIs

        Raises:
            RuntimeError: If authentication fails
        """
        creds: Credentials | None = None
        token_path = self.credentials_path.parent / "token.json"

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
                if not self.credentials_path.exists():
                    raise RuntimeError(
                        f"Credentials file not found: {self.credentials_path}\n"
                        "Please download OAuth2 credentials from Google Cloud Console:\n"
                        "1. Go to https://console.cloud.google.com/\n"
                        "2. Create a project or select an existing one\n"
                        "3. Enable the Google Drive API\n"
                        "4. Create OAuth2 credentials (Desktop app)\n"
                        "5. Download the credentials JSON file"
                    )

                logger.info("Opening browser for authentication...")
                flow = InstalledAppFlow.from_client_secrets_file(str(self.credentials_path), SCOPES)
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            logger.debug("Saving token for future use")
            token_path.write_text(creds.to_json())

        return creds

    @cached_property
    def drive(self) -> Any:
        """Get Google Drive API service.

        Returns:
            Google Drive API v3 service object

        Raises:
            RuntimeError: If service creation fails
        """
        try:
            service = build("drive", "v3", credentials=self._credentials)
            logger.debug("Successfully authenticated with Google Drive")
            return service
        except Exception as e:
            raise RuntimeError(f"Failed to build Google Drive service: {e}")

    @cached_property
    def docs(self) -> Any:
        """Get Google Docs API service.

        Returns:
            Google Docs API v1 service object

        Raises:
            RuntimeError: If service creation fails
        """
        try:
            service = build("docs", "v1", credentials=self._credentials)
            logger.debug("Successfully authenticated with Google Docs")
            return service
        except Exception as e:
            raise RuntimeError(f"Failed to build Google Docs service: {e}")
