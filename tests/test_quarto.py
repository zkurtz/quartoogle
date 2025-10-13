"""Tests for quarto module."""

from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from quartoogle.quarto import compile_to_docx


def test_compile_to_docx_quarto_not_installed(mocker: MockerFixture) -> None:
    """Test that we get a proper error when quarto is not installed."""
    mock_render = mocker.patch("quartoogle.quarto.render")
    mock_render.side_effect = FileNotFoundError("Unable to find quarto command line tools.")

    with pytest.raises(FileNotFoundError) as exc_info:
        compile_to_docx(Path("test.qmd"))

    assert "quarto" in str(exc_info.value).lower()


def test_compile_to_docx_compilation_failure(mocker: MockerFixture) -> None:
    """Test handling of quarto compilation failure."""
    mock_render = mocker.patch("quartoogle.quarto.render")
    mock_render.side_effect = RuntimeError("Compilation error")

    with pytest.raises(RuntimeError) as exc_info:
        compile_to_docx(Path("test.qmd"))

    assert "error" in str(exc_info.value).lower()


def test_compile_to_docx_output_not_found(mocker: MockerFixture) -> None:
    """Test handling when output file is not created."""
    mock_render = mocker.patch("quartoogle.quarto.render")
    # Simulate successful render but no output file created
    mock_render.return_value = None

    with pytest.raises(RuntimeError) as exc_info:
        compile_to_docx(Path("test.qmd"))

    assert "not found" in str(exc_info.value).lower()


def test_compile_to_docx_success(tmp_path: Path, mocker: MockerFixture) -> None:
    """Test successful compilation."""
    source = tmp_path / "test.qmd"
    source.write_text("# Test")
    docx = tmp_path / "test.docx"
    docx.write_bytes(b"fake docx")

    mock_render = mocker.patch("quartoogle.quarto.render")
    # Mock successful render
    mock_render.return_value = None

    result = compile_to_docx(source)

    assert result == docx
    assert result.exists()
    # Verify render was called with correct arguments
    mock_render.assert_called_once_with(str(source), output_format="docx")
