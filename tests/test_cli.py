"""Tests for quartoogle CLI."""

from click.testing import CliRunner

from quartoogle.cli import main


def test_cli_help():
    """Test that CLI help works."""
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])

    # --help exits with code 0
    assert result.exit_code == 0
    assert "Compile quarto docs directly to Google Drive" in result.output


def test_cli_missing_source():
    """Test that CLI fails when source file is missing."""
    runner = CliRunner()
    result = runner.invoke(main, ["nonexistent.qmd", "--output", "test"])

    # Should exit with error code
    assert result.exit_code != 0


def test_cli_missing_output_arg():
    """Test that CLI fails when --output is not provided."""
    runner = CliRunner()
    result = runner.invoke(main, ["test.qmd"])

    # Should exit with error code (click error)
    assert result.exit_code == 2


def test_cli_invalid_file_extension(tmp_path):
    """Test that CLI fails when source file is not .qmd."""
    # Create a non-.qmd file
    test_file = tmp_path / "test.txt"
    test_file.write_text("test")

    runner = CliRunner()
    result = runner.invoke(main, [str(test_file), "--output", "test"])

    assert result.exit_code == 1
