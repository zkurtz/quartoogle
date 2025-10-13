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
    mocker.patch("quartoogle.google.OAuth2Credentials.from_authorized_user_file", return_value=mock_creds)
    mock_build = mocker.patch("quartoogle.google.build")

    mock_drive_service = mocker.Mock()
    mock_build.return_value = mock_drive_service

    services = Services(Path("/fake/credentials.json"))
    drive_service = services.drive

    # Verify build was called with correct parameters
    mock_build.assert_called_once_with("drive", "v3", credentials=mock_creds)
    assert drive_service == mock_drive_service
