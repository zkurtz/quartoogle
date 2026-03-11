"""Tests for quarto module."""

from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from quartoogle.quarto import compile_quarto, compile_to_docx


def test_compile_to_docx_quarto_not_installed(mocker: MockerFixture) -> None:
    """Test that we get a proper error when quarto is not installed."""
    mock_render = mocker.patch("quartoogle.quarto.render")
    mock_render.side_effect = FileNotFoundError("Unable to find quarto command line tools.")

    with pytest.raises(FileNotFoundError) as exc_info:
        compile_quarto(Path("test.qmd"))

    assert "quarto" in str(exc_info.value).lower()


def test_compile_to_docx_compilation_failure(mocker: MockerFixture) -> None:
    """Test handling of quarto compilation failure."""
    mock_render = mocker.patch("quartoogle.quarto.render")
    mock_render.side_effect = RuntimeError("Compilation error")

    with pytest.raises(RuntimeError) as exc_info:
        compile_quarto(Path("test.qmd"))

    assert "error" in str(exc_info.value).lower()


def test_compile_to_docx_output_not_found(mocker: MockerFixture) -> None:
    """Test handling when output file is not created."""
    mock_render = mocker.patch("quartoogle.quarto.render")
    # Simulate successful render but no output file created
    mock_render.return_value = None

    with pytest.raises(RuntimeError) as exc_info:
        compile_quarto(Path("test.qmd"))

    assert "not found" in str(exc_info.value).lower()


def test_stale_output_file_deleted_before_compilation(tmp_path: Path, mocker: MockerFixture) -> None:
    """Test that stale output files are deleted before compilation.

    This prevents uploading an old report if the current compilation fails.
    Reproduces GitHub issue #42.
    """
    source = tmp_path / "test.qmd"
    source.write_text("# Test")
    pdf = tmp_path / "test.pdf"
    # Create an old/stale PDF file
    pdf.write_bytes(b"stale pdf content")
    assert pdf.exists()

    mock_render = mocker.patch("quartoogle.quarto.render")
    # Simulate render failing silently (doesn't raise, but doesn't create file)
    mock_render.return_value = None

    with pytest.raises(RuntimeError) as exc_info:
        compile_quarto(source)

    # The error should indicate no output file, not return the stale file
    assert "not found" in str(exc_info.value).lower()
    # The stale file should have been deleted
    assert not pdf.exists()


def test_stale_output_file_replaced_on_success(tmp_path: Path, mocker: MockerFixture) -> None:
    """Test that stale output files are replaced when compilation succeeds."""
    source = tmp_path / "test.qmd"
    source.write_text("# Test")
    pdf = tmp_path / "test.pdf"
    # Create an old/stale PDF file
    pdf.write_bytes(b"stale pdf content")

    def mock_render_side_effect(*args, **kwargs) -> None:
        # Simulate successful render by creating new file content
        pdf.write_bytes(b"new pdf content")

    mock_render = mocker.patch("quartoogle.quarto.render")
    mock_render.side_effect = mock_render_side_effect

    result = compile_quarto(source)

    assert result == pdf
    assert result.exists()
    assert result.read_bytes() == b"new pdf content"


def test_compile_to_docx_success(tmp_path: Path, mocker: MockerFixture) -> None:
    """Test successful compilation to PDF (default)."""
    source = tmp_path / "test.qmd"
    source.write_text("# Test")
    pdf = tmp_path / "test.pdf"

    def mock_render_side_effect(*args, **kwargs) -> None:
        pdf.write_bytes(b"fake pdf")

    mock_render = mocker.patch("quartoogle.quarto.render")
    mock_render.side_effect = mock_render_side_effect

    result = compile_quarto(source)

    assert result == pdf
    assert result.exists()
    # Verify render was called with correct arguments (default is pdf)
    mock_render.assert_called_once_with(str(source), output_format="pdf", quiet=True)


def test_compile_quarto_with_docx(tmp_path: Path, mocker: MockerFixture) -> None:
    """Test compilation to docx format."""
    source = tmp_path / "test.qmd"
    source.write_text("# Test")
    docx = tmp_path / "test.docx"

    def mock_render_side_effect(*args, **kwargs) -> None:
        docx.write_bytes(b"fake docx")

    mock_render = mocker.patch("quartoogle.quarto.render")
    mock_render.side_effect = mock_render_side_effect

    result = compile_quarto(source, "docx")

    assert result == docx
    assert result.exists()
    # Verify render was called with correct arguments
    mock_render.assert_called_once_with(str(source), output_format="docx", quiet=True)


def test_compile_to_docx_backward_compatibility(tmp_path: Path, mocker: MockerFixture) -> None:
    """Test that compile_to_docx wrapper still works."""
    source = tmp_path / "test.qmd"
    source.write_text("# Test")
    docx = tmp_path / "test.docx"

    def mock_render_side_effect(*args, **kwargs) -> None:
        docx.write_bytes(b"fake docx")

    mock_render = mocker.patch("quartoogle.quarto.render")
    mock_render.side_effect = mock_render_side_effect

    result = compile_to_docx(source)

    assert result == docx
    assert result.exists()
    # Verify render was called with docx format
    mock_render.assert_called_once_with(str(source), output_format="docx", quiet=True)
