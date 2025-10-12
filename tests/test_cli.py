"""Tests for quartoogle CLI."""

import sys
from io import StringIO
from pathlib import Path
import pytest

from quartoogle.cli import main


def test_cli_help(monkeypatch):
    """Test that CLI help works."""
    monkeypatch.setattr(sys, 'argv', ['quartoogle', '--help'])
    
    with pytest.raises(SystemExit) as exc_info:
        main()
    
    # --help exits with code 0
    assert exc_info.value.code == 0


def test_cli_missing_source(monkeypatch):
    """Test that CLI fails when source file is missing."""
    monkeypatch.setattr(sys, 'argv', ['quartoogle', 'nonexistent.qmd', '--output', 'test'])
    
    with pytest.raises(SystemExit) as exc_info:
        main()
    
    # Should exit with error code
    assert exc_info.value.code == 1


def test_cli_missing_output_arg(monkeypatch):
    """Test that CLI fails when --output is not provided."""
    monkeypatch.setattr(sys, 'argv', ['quartoogle', 'test.qmd'])
    
    with pytest.raises(SystemExit) as exc_info:
        main()
    
    # Should exit with error code (argparse error)
    assert exc_info.value.code == 2


def test_cli_invalid_file_extension(monkeypatch, tmp_path):
    """Test that CLI fails when source file is not .qmd."""
    # Create a non-.qmd file
    test_file = tmp_path / "test.txt"
    test_file.write_text("test")
    
    monkeypatch.setattr(sys, 'argv', ['quartoogle', str(test_file), '--output', 'test'])
    
    with pytest.raises(SystemExit) as exc_info:
        main()
    
    assert exc_info.value.code == 1
