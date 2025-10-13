"""Tests for quartoogle CLI."""

from pathlib import Path

from click.testing import CliRunner

from quartoogle.cli import main


def test_cli_help() -> None:
    """Test that CLI help works."""
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])

    # --help exits with code 0
    assert result.exit_code == 0
    assert "Compile quarto docs directly to Google Drive" in result.output


def test_cli_missing_source() -> None:
    """Test that CLI fails when source file is missing."""
    runner = CliRunner()
    result = runner.invoke(main, ["nonexistent.qmd", "--folder-id", "1a2b3c4d5e6f7g8h9i0j"])

    # Should exit with error code
    assert result.exit_code != 0


def test_cli_missing_output_arg() -> None:
    """Test that CLI fails when --folder-id is not provided."""
    runner = CliRunner()
    result = runner.invoke(main, ["test.qmd"])

    # Should exit with error code (click error)
    assert result.exit_code == 2


def test_cli_with_to_option(tmp_path: Path) -> None:
    """Test that CLI accepts --to option for format."""
    # Create a .qmd file
    test_file = tmp_path / "test.qmd"
    test_file.write_text("# Test")

    runner = CliRunner()
    result = runner.invoke(main, [str(test_file), "--folder-id", "1a2b3c4d5e6f7g8h9i0j", "--to", "html"])

    # Should fail (no real quarto/google creds) but should accept the --to option
    # The error should not be about the --to option
    assert "--to" not in result.output or result.exit_code != 2


def test_cli_invalid_file_extension(tmp_path: Path) -> None:
    """Test that CLI fails when source file is not .qmd."""
    # Create a non-.qmd file
    test_file = tmp_path / "test.txt"
    test_file.write_text("test")

    runner = CliRunner()
    result = runner.invoke(main, [str(test_file), "--folder-id", "1a2b3c4d5e6f7g8h9i0j"])

    assert result.exit_code == 1
