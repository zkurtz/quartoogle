"""Tests for Google Drive module."""

from pathlib import Path
import pytest
from unittest.mock import Mock, patch, MagicMock

from quartoogle.gdrive import authenticate, find_or_create_folder, upload_file


def test_authenticate_missing_credentials():
    """Test authentication fails with missing credentials file."""
    with patch('quartoogle.gdrive.Path.exists', return_value=False):
        with patch('quartoogle.gdrive.Credentials.from_authorized_user_file') as mock_creds:
            mock_creds.side_effect = FileNotFoundError()
            
            with pytest.raises(RuntimeError) as exc_info:
                authenticate(Path("nonexistent.json"))
            
            assert "not found" in str(exc_info.value).lower()


def test_find_or_create_folder_existing(tmp_path):
    """Test finding an existing folder."""
    mock_service = Mock()
    mock_files = Mock()
    mock_list = Mock()
    
    mock_list.execute.return_value = {
        'files': [{'id': 'folder123', 'name': 'TestFolder'}]
    }
    mock_files.list.return_value = mock_list
    mock_service.files.return_value = mock_files
    
    result = find_or_create_folder(mock_service, "TestFolder")
    
    assert result == 'folder123'


def test_find_or_create_folder_new(tmp_path):
    """Test creating a new folder."""
    mock_service = Mock()
    mock_files = Mock()
    mock_list = Mock()
    mock_create = Mock()
    
    # No existing folders
    mock_list.execute.return_value = {'files': []}
    mock_files.list.return_value = mock_list
    
    # Create new folder
    mock_create.execute.return_value = {'id': 'newfolder123'}
    mock_files.create.return_value = mock_create
    
    mock_service.files.return_value = mock_files
    
    result = find_or_create_folder(mock_service, "NewFolder")
    
    assert result == 'newfolder123'


def test_upload_file_with_folder_name(tmp_path):
    """Test uploading file to a folder by name."""
    test_file = tmp_path / "test.docx"
    test_file.write_bytes(b"fake docx")
    
    mock_service = Mock()
    mock_files = Mock()
    
    # Mock find_or_create_folder
    with patch('quartoogle.gdrive.find_or_create_folder') as mock_find:
        mock_find.return_value = 'folder123'
        
        # Mock file creation
        mock_create = Mock()
        mock_create.execute.return_value = {
            'id': 'file123',
            'webViewLink': 'https://docs.google.com/document/d/file123/edit'
        }
        mock_files.create.return_value = mock_create
        mock_service.files.return_value = mock_files
        
        result = upload_file(mock_service, test_file, "TestFolder")
        
        assert "docs.google.com" in result
        assert "file123" in result


def test_upload_file_with_folder_id(tmp_path):
    """Test uploading file to a folder by ID."""
    test_file = tmp_path / "test.docx"
    test_file.write_bytes(b"fake docx")
    
    mock_service = Mock()
    mock_files = Mock()
    
    # Mock file creation
    mock_create = Mock()
    mock_create.execute.return_value = {
        'id': 'file123',
        'webViewLink': 'https://docs.google.com/document/d/file123/edit'
    }
    mock_files.create.return_value = mock_create
    mock_service.files.return_value = mock_files
    
    # Use a long alphanumeric string as folder ID
    result = upload_file(mock_service, test_file, "a1b2c3d4e5f6g7h8i9j0k1")
    
    assert "docs.google.com" in result
