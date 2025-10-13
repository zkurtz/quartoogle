"""Tests for quartoogle API."""

from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from quartoogle.api import publish


def test_publish_invalid_file_extension() -> None:
    """Test that publish raises ValueError for non-.qmd files."""
    with pytest.raises(ValueError) as exc_info:
        publish("test.txt", folder_id="1a2b3c4d5e6f7g8h9i0j")

    assert ".qmd" in str(exc_info.value)
    assert "test.txt" in str(exc_info.value)


def test_publish_success(tmp_path: Path, mocker: MockerFixture) -> None:
    """Test successful publish operation."""
    # Create a .qmd file
    source = tmp_path / "test.qmd"
    source.write_text("# Test")

    # Create a fake compiled output
    pdf = tmp_path / "test.pdf"
    pdf.write_bytes(b"fake pdf")

    # Mock the dependencies
    mock_compile = mocker.patch("quartoogle.api.compile_quarto")
    mock_compile.return_value = pdf

    mock_get_service = mocker.patch("quartoogle.api.get_drive_service")
    mock_service = mocker.Mock()
    mock_get_service.return_value = mock_service

    mock_upload = mocker.patch("quartoogle.api.upload_file")
    mock_upload.return_value = ("file123", "https://docs.google.com/document/d/file123/edit")

    # Call publish
    file_id, file_url = publish(source, folder_id="1a2b3c4d5e6f7g8h9i0j")

    # Verify the results
    assert file_id == "file123"
    assert "file123" in file_url

    # Verify the mocks were called correctly
    mock_compile.assert_called_once_with(source, "pdf")
    mock_get_service.assert_called_once()
    mock_upload.assert_called_once_with(mock_service, pdf, "1a2b3c4d5e6f7g8h9i0j")


def test_publish_with_custom_format(tmp_path: Path, mocker: MockerFixture) -> None:
    """Test publish with custom output format."""
    # Create a .qmd file
    source = tmp_path / "test.qmd"
    source.write_text("# Test")

    # Create a fake compiled output
    docx = tmp_path / "test.docx"
    docx.write_bytes(b"fake docx")

    # Mock the dependencies
    mock_compile = mocker.patch("quartoogle.api.compile_quarto")
    mock_compile.return_value = docx

    mock_get_service = mocker.patch("quartoogle.api.get_drive_service")
    mock_service = mocker.Mock()
    mock_get_service.return_value = mock_service

    mock_upload = mocker.patch("quartoogle.api.upload_file")
    mock_upload.return_value = ("file123", "https://docs.google.com/document/d/file123/edit")

    # Call publish with docx format
    file_id, file_url = publish(source, folder_id="1a2b3c4d5e6f7g8h9i0j", output_format="docx")

    # Verify compile_quarto was called with docx format
    mock_compile.assert_called_once_with(source, "docx")


def test_publish_with_custom_credentials(tmp_path: Path, mocker: MockerFixture) -> None:
    """Test publish with custom credentials path."""
    # Create a .qmd file
    source = tmp_path / "test.qmd"
    source.write_text("# Test")

    # Create fake credentials path
    creds = tmp_path / "custom_creds.json"

    # Create a fake compiled output
    pdf = tmp_path / "test.pdf"
    pdf.write_bytes(b"fake pdf")

    # Mock the dependencies
    mock_compile = mocker.patch("quartoogle.api.compile_quarto")
    mock_compile.return_value = pdf

    mock_get_service = mocker.patch("quartoogle.api.get_drive_service")
    mock_service = mocker.Mock()
    mock_get_service.return_value = mock_service

    mock_upload = mocker.patch("quartoogle.api.upload_file")
    mock_upload.return_value = ("file123", "https://docs.google.com/document/d/file123/edit")

    # Call publish with custom credentials
    publish(source, folder_id="1a2b3c4d5e6f7g8h9i0j", credentials=creds)

    # Verify get_drive_service was called with custom credentials path
    mock_get_service.assert_called_once_with(creds)


def test_publish_with_string_paths(tmp_path: Path, mocker: MockerFixture) -> None:
    """Test that publish accepts string paths."""
    # Create a .qmd file
    source = tmp_path / "test.qmd"
    source.write_text("# Test")

    # Create a fake compiled output
    pdf = tmp_path / "test.pdf"
    pdf.write_bytes(b"fake pdf")

    # Mock the dependencies
    mock_compile = mocker.patch("quartoogle.api.compile_quarto")
    mock_compile.return_value = pdf

    mock_get_service = mocker.patch("quartoogle.api.get_drive_service")
    mock_service = mocker.Mock()
    mock_get_service.return_value = mock_service

    mock_upload = mocker.patch("quartoogle.api.upload_file")
    mock_upload.return_value = ("file123", "https://docs.google.com/document/d/file123/edit")

    # Call publish with string path
    file_id, file_url = publish(str(source), folder_id="1a2b3c4d5e6f7g8h9i0j")

    # Verify it worked
    assert file_id == "file123"
    assert "file123" in file_url
