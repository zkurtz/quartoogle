"""Tests for quarto module."""

import subprocess
from pathlib import Path
import pytest

from quartoogle.quarto import compile_to_docx


def test_compile_to_docx_quarto_not_installed(mocker):
    """Test that we get a proper error when quarto is not installed."""
    mock_run = mocker.patch('subprocess.run')
    mock_run.side_effect = FileNotFoundError()
    
    with pytest.raises(RuntimeError) as exc_info:
        compile_to_docx(Path("test.qmd"))
    
    assert "not installed" in str(exc_info.value).lower()


def test_compile_to_docx_compilation_failure(mocker):
    """Test handling of quarto compilation failure."""
    mock_run = mocker.patch('subprocess.run')
    
    # Mock successful quarto check
    mock_check = mocker.Mock()
    mock_check.returncode = 0
    
    # Mock failed compilation
    mock_compile = mocker.Mock()
    mock_compile.returncode = 1
    mock_compile.stderr = "Compilation error"
    
    mock_run.side_effect = [mock_check, mock_compile]
    
    with pytest.raises(RuntimeError) as exc_info:
        compile_to_docx(Path("test.qmd"))
    
    assert "failed" in str(exc_info.value).lower()


def test_compile_to_docx_output_not_found(mocker):
    """Test handling when output file is not created."""
    mock_run = mocker.patch('subprocess.run')
    
    # Mock successful runs
    mock_result = mocker.Mock()
    mock_result.returncode = 0
    mock_result.stdout = "Success"
    mock_run.return_value = mock_result
    
    with pytest.raises(RuntimeError) as exc_info:
        compile_to_docx(Path("test.qmd"))
    
    assert "not found" in str(exc_info.value).lower()


def test_compile_to_docx_success(tmp_path, mocker):
    """Test successful compilation."""
    source = tmp_path / "test.qmd"
    source.write_text("# Test")
    docx = tmp_path / "test.docx"
    docx.write_bytes(b"fake docx")
    
    mock_run = mocker.patch('subprocess.run')
    
    # Mock successful runs
    mock_result = mocker.Mock()
    mock_result.returncode = 0
    mock_result.stdout = "Success"
    mock_run.return_value = mock_result
    
    result = compile_to_docx(source)
    
    assert result == docx
    assert result.exists()
