"""Tests for Google API services module."""

from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from quartoogle.google import Services


def test_services_missing_credentials(mocker: MockerFixture) -> None:
    """Test Services fails with missing credentials file."""
    mocker.patch("quartoogle.google.Path.exists", return_value=False)

    services = Services(Path("nonexistent.json"))

    with pytest.raises(RuntimeError) as exc_info:
        # Access _credentials to trigger authentication
        _ = services._credentials

    assert "not found" in str(exc_info.value).lower()


def test_services_drive_property(mocker: MockerFixture) -> None:
    """Test Services.drive property creates Drive service."""
    mock_creds = mocker.Mock()
    mock_creds.valid = True

    mocker.patch("quartoogle.google.Path.exists", return_value=True)
    mocker.patch("quartoogle.google.Credentials.from_authorized_user_file", return_value=mock_creds)
    mock_build = mocker.patch("quartoogle.google.build")

    mock_drive_service = mocker.Mock()
    mock_build.return_value = mock_drive_service

    services = Services(Path("/fake/credentials.json"))
    drive_service = services.drive

    # Verify build was called with correct parameters
    mock_build.assert_called_once_with("drive", "v3", credentials=mock_creds)
    assert drive_service == mock_drive_service


def test_services_docs_property(mocker: MockerFixture) -> None:
    """Test Services.docs property creates Docs service."""
    mock_creds = mocker.Mock()
    mock_creds.valid = True

    mocker.patch("quartoogle.google.Path.exists", return_value=True)
    mocker.patch("quartoogle.google.Credentials.from_authorized_user_file", return_value=mock_creds)
    mock_build = mocker.patch("quartoogle.google.build")

    mock_docs_service = mocker.Mock()
    mock_build.return_value = mock_docs_service

    services = Services(Path("/fake/credentials.json"))
    docs_service = services.docs

    # Verify build was called with correct parameters
    mock_build.assert_called_once_with("docs", "v1", credentials=mock_creds)
    assert docs_service == mock_docs_service


def test_services_cached_properties(mocker: MockerFixture) -> None:
    """Test that services are cached and credentials are only loaded once."""
    mock_creds = mocker.Mock()
    mock_creds.valid = True

    mocker.patch("quartoogle.google.Path.exists", return_value=True)
    mock_from_file = mocker.patch("quartoogle.google.Credentials.from_authorized_user_file", return_value=mock_creds)
    mock_build = mocker.patch("quartoogle.google.build")

    services = Services(Path("/fake/credentials.json"))

    # Access drive multiple times
    _ = services.drive
    _ = services.drive

    # Access docs multiple times
    _ = services.docs
    _ = services.docs

    # Credentials should only be loaded once
    mock_from_file.assert_called_once()

    # Each service should only be built once
    assert mock_build.call_count == 2  # Once for drive, once for docs
