"""Quartoogle Python API - Programmatic interface for compiling quarto docs to Google Drive."""

import logging
from pathlib import Path

from quartoogle import constants
from quartoogle.gdrive import get_drive_service, upload_file
from quartoogle.quarto import compile_quarto

logger = logging.getLogger(__name__)


def publish(
    source: str | Path,
    folder_id: str,
    output_format: str = "pdf",
    credentials: str | Path | None = None,
) -> tuple[str, str]:
    """Compile a quarto document and upload it to Google Drive.

    This is the main programmatic API for quartoogle. It compiles a .qmd file
    to the specified format and uploads it to Google Drive.

    Args:
        source: Path to the .qmd source file
        folder_id: Google Drive folder ID where the file will be uploaded.
                   You must manually create the folder in Google Drive and obtain its ID from the URL.
        output_format: Output format (e.g., 'pdf', 'docx', 'html'). Default is 'pdf'.
        credentials: Path to Google OAuth2 credentials JSON file.
                    If not provided, uses the default location at ~/.config/google/drive/credentials.json

    Returns:
        A tuple of (file_id, web_view_link) for the uploaded file

    Raises:
        ValueError: If source file is not a .qmd file
        RuntimeError: If compilation or upload fails

    Example:
        >>> import quartoogle
        >>> file_id, url = quartoogle.publish("report.qmd", folder_id="1a2b3c4d5e6f7g8h9i0j")
        >>> print(f"Uploaded: {url}")
    """
    # Convert to Path objects
    source_path = Path(source)
    credentials_path = Path(credentials) if credentials is not None else constants.CREDS_PATH

    # Validate source file extension
    if source_path.suffix != ".qmd":
        raise ValueError(f"Source file must be a .qmd file, got: {source_path}")

    # Compile the quarto document
    logger.info(f"Compiling {source_path} to {output_format}...")
    output_path = compile_quarto(source_path, output_format)
    logger.info(f"Successfully compiled to: {output_path}")

    # Authenticate with Google Drive
    logger.info("Authenticating with Google Drive...")
    drive_service = get_drive_service(credentials_path)

    # Upload to Google Drive
    logger.info(f"Uploading to Google Drive folder: {folder_id}")
    file_id, file_url = upload_file(drive_service, output_path, folder_id)

    logger.info("Upload complete!")
    logger.info(f"View your document at: {file_url}")

    return file_id, file_url
