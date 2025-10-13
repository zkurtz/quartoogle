"""Tests for Google Drive module."""

from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from quartoogle.gdrive import find_or_create_folder, get_drive_service, upload_file


def test_get_drive_service_missing_credentials(mocker: MockerFixture) -> None:
    """Test get_drive_service fails with missing credentials file."""
    mocker.patch("quartoogle.gdrive.Path.exists", return_value=False)

    with pytest.raises(RuntimeError) as exc_info:
        get_drive_service(Path("nonexistent.json"))

    assert "not found" in str(exc_info.value).lower()


def test_get_drive_service_creates_service(mocker: MockerFixture) -> None:
    """Test get_drive_service creates Drive service."""
    mock_creds = mocker.Mock()
    mock_creds.valid = True

    mocker.patch("quartoogle.gdrive.Path.exists", return_value=True)
    mocker.patch("quartoogle.gdrive.OAuth2Credentials.from_authorized_user_file", return_value=mock_creds)
    mock_build = mocker.patch("quartoogle.gdrive.build")

    mock_drive_service = mocker.Mock()
    mock_build.return_value = mock_drive_service

    drive_service = get_drive_service(Path("/fake/credentials.json"))

    # Verify build was called with correct parameters
    mock_build.assert_called_once_with("drive", "v3", credentials=mock_creds)
    assert drive_service == mock_drive_service


def test_find_or_create_folder_existing(tmp_path: Path, mocker: MockerFixture) -> None:
    """Test finding an existing folder."""
    mock_service = mocker.Mock()
    mock_files = mocker.Mock()
    mock_list = mocker.Mock()

    mock_list.execute.return_value = {"files": [{"id": "folder123", "name": "TestFolder"}]}
    mock_files.list.return_value = mock_list
    mock_service.files.return_value = mock_files

    result = find_or_create_folder(mock_service, "TestFolder")

    assert result == "folder123"


def test_find_or_create_folder_new(tmp_path: Path, mocker: MockerFixture) -> None:
    """Test creating a new folder."""
    mock_service = mocker.Mock()
    mock_files = mocker.Mock()
    mock_list = mocker.Mock()
    mock_create = mocker.Mock()

    # No existing folders
    mock_list.execute.return_value = {"files": []}
    mock_files.list.return_value = mock_list

    # Create new folder
    mock_create.execute.return_value = {"id": "newfolder123"}
    mock_files.create.return_value = mock_create

    mock_service.files.return_value = mock_files

    result = find_or_create_folder(mock_service, "NewFolder")

    assert result == "newfolder123"


def test_upload_file_with_folder_id(tmp_path: Path, mocker: MockerFixture) -> None:
    """Test uploading file to a folder by ID."""
    test_file = tmp_path / "test.docx"
    test_file.write_bytes(b"fake docx")

    mock_service = mocker.Mock()
    mock_files = mocker.Mock()

    # Mock file creation
    mock_create = mocker.Mock()
    mock_create.execute.return_value = {
        "id": "file123",
        "webViewLink": "https://docs.google.com/document/d/file123/edit",
    }
    mock_files.create.return_value = mock_create
    mock_service.files.return_value = mock_files

    # Use a folder ID
    file_id, file_url = upload_file(mock_service, test_file, "1a2b3c4d5e6f7g8h9i0j")

    assert file_id == "file123"
    assert "docs.google.com" in file_url


def test_upload_file_adds_timestamp_to_name(tmp_path: Path, mocker: MockerFixture) -> None:
    """Test that uploaded file name includes timestamp suffix."""
    test_file = tmp_path / "report.docx"
    test_file.write_bytes(b"fake docx")

    mock_service = mocker.Mock()
    mock_files = mocker.Mock()

    # Mock file creation
    mock_create = mocker.Mock()
    mock_create.execute.return_value = {
        "id": "file123",
        "webViewLink": "https://docs.google.com/document/d/file123/edit",
    }
    mock_files.create.return_value = mock_create
    mock_service.files.return_value = mock_files

    # Call upload_file with folder ID
    file_id, file_url = upload_file(mock_service, test_file, "1a2b3c4d5e6f7g8h9i0j")

    # Verify the file was created with timestamp
    mock_files.create.assert_called_once()
    call_args = mock_files.create.call_args
    file_metadata = call_args.kwargs["body"]

    # Check that the name has timestamp format: report_YYYY-MM-DD_HH-MM.docx
    import re

    pattern = r"^report_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}\.docx$"
    assert re.match(pattern, file_metadata["name"]), f"Expected timestamp format, got: {file_metadata['name']}"

    # Verify the name starts with the original stem
    assert file_metadata["name"].startswith("report_")
    # Verify it ends with the correct extension
    assert file_metadata["name"].endswith(".docx")
