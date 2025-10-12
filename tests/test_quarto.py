"""Tests for quarto module."""

import subprocess
from pathlib import Path
import pytest
from unittest.mock import Mock, patch, MagicMock

from quartoogle.quarto import compile_to_docx


def test_compile_to_docx_quarto_not_installed():
    """Test that we get a proper error when quarto is not installed."""
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = FileNotFoundError()
        
        with pytest.raises(RuntimeError) as exc_info:
            compile_to_docx(Path("test.qmd"))
        
        assert "not installed" in str(exc_info.value).lower()


def test_compile_to_docx_compilation_failure():
    """Test handling of quarto compilation failure."""
    with patch('subprocess.run') as mock_run:
        # Mock successful quarto check
        mock_check = Mock()
        mock_check.returncode = 0
        
        # Mock failed compilation
        mock_compile = Mock()
        mock_compile.returncode = 1
        mock_compile.stderr = "Compilation error"
        
        mock_run.side_effect = [mock_check, mock_compile]
        
        with pytest.raises(RuntimeError) as exc_info:
            compile_to_docx(Path("test.qmd"))
        
        assert "failed" in str(exc_info.value).lower()


def test_compile_to_docx_output_not_found():
    """Test handling when output file is not created."""
    with patch('subprocess.run') as mock_run:
        # Mock successful runs
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Success"
        mock_run.return_value = mock_result
        
        with pytest.raises(RuntimeError) as exc_info:
            compile_to_docx(Path("test.qmd"))
        
        assert "not found" in str(exc_info.value).lower()


def test_compile_to_docx_success(tmp_path):
    """Test successful compilation."""
    source = tmp_path / "test.qmd"
    source.write_text("# Test")
    docx = tmp_path / "test.docx"
    docx.write_bytes(b"fake docx")
    
    with patch('subprocess.run') as mock_run:
        # Mock successful runs
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Success"
        mock_run.return_value = mock_result
        
        result = compile_to_docx(source)
        
        assert result == docx
        assert result.exists()
