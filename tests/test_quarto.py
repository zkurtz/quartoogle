"""Tests for quarto module."""

from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from quartoogle.quarto import compile_quarto, compile_to_docx


def test_compile_to_docx_quarto_not_installed(mocker: MockerFixture) -> None:
    """Test that we get a proper error when quarto is not installed."""
    mock_run = mocker.patch("subprocess.run")
    mock_run.side_effect = FileNotFoundError()

    with pytest.raises(RuntimeError) as exc_info:
        compile_quarto(Path("test.qmd"))

    assert "not installed" in str(exc_info.value).lower()


def test_compile_to_docx_compilation_failure(mocker: MockerFixture) -> None:
    """Test handling of quarto compilation failure."""
    mock_run = mocker.patch("subprocess.run")

    # Mock successful quarto check
    mock_check = mocker.Mock()
    mock_check.returncode = 0

    # Mock failed compilation
    mock_compile = mocker.Mock()
    mock_compile.returncode = 1
    mock_compile.stderr = "Compilation error"

    mock_run.side_effect = [mock_check, mock_compile]

    with pytest.raises(RuntimeError) as exc_info:
        compile_quarto(Path("test.qmd"))

    assert "failed" in str(exc_info.value).lower()


def test_compile_to_docx_output_not_found(mocker: MockerFixture) -> None:
    """Test handling when output file is not created."""
    mock_run = mocker.patch("subprocess.run")

    # Mock successful runs
    mock_result = mocker.Mock()
    mock_result.returncode = 0
    mock_result.stdout = "Success"
    mock_run.return_value = mock_result

    with pytest.raises(RuntimeError) as exc_info:
        compile_quarto(Path("test.qmd"))

    assert "not found" in str(exc_info.value).lower()


def test_compile_to_docx_success(tmp_path: Path, mocker: MockerFixture) -> None:
    """Test successful compilation."""
    source = tmp_path / "test.qmd"
    source.write_text("# Test")
    pdf = tmp_path / "test.pdf"
    pdf.write_bytes(b"fake pdf")

    mock_run = mocker.patch("subprocess.run")

    # Mock successful runs
    mock_result = mocker.Mock()
    mock_result.returncode = 0
    mock_result.stdout = "Success"
    mock_run.return_value = mock_result

    result = compile_quarto(source)

    assert result == pdf
    assert result.exists()


def test_compile_quarto_with_docx(tmp_path: Path, mocker: MockerFixture) -> None:
    """Test compilation to docx format."""
    source = tmp_path / "test.qmd"
    source.write_text("# Test")
    docx = tmp_path / "test.docx"
    docx.write_bytes(b"fake docx")

    mock_run = mocker.patch("subprocess.run")

    # Mock successful runs
    mock_result = mocker.Mock()
    mock_result.returncode = 0
    mock_result.stdout = "Success"
    mock_run.return_value = mock_result

    result = compile_quarto(source, "docx")

    assert result == docx
    assert result.exists()


def test_compile_to_docx_backward_compatibility(tmp_path: Path, mocker: MockerFixture) -> None:
    """Test that compile_to_docx wrapper still works."""
    source = tmp_path / "test.qmd"
    source.write_text("# Test")
    docx = tmp_path / "test.docx"
    docx.write_bytes(b"fake docx")

    mock_run = mocker.patch("subprocess.run")

    # Mock successful runs
    mock_result = mocker.Mock()
    mock_result.returncode = 0
    mock_result.stdout = "Success"
    mock_run.return_value = mock_result

    result = compile_to_docx(source)

    assert result == docx
    assert result.exists()

