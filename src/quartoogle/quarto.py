"""Quarto compilation utilities."""

import logging
from pathlib import Path

from quarto import render

logger = logging.getLogger(__name__)


def compile_quarto(source_path: Path, output_format: str = "pdf") -> Path:
    """Compile a quarto source file to the specified format.

    Args:
        source_path: Path to the .qmd source file
        output_format: Output format (e.g., 'pdf', 'docx', 'html'). Default is 'pdf'.

    Returns:
        Path to the generated output file

    Raises:
        RuntimeError: If quarto is not installed or compilation fails
    """
    logger.debug(f"Rendering {source_path} to {output_format}")

    # Use quiet mode unless logging level is DEBUG
    quiet = logger.getEffectiveLevel() > logging.DEBUG
    render(str(source_path), output_format=output_format, quiet=quiet)

    # Determine output path (quarto creates output file next to source)
    output_path = source_path.with_suffix(f".{output_format}")

    if not output_path.exists():
        raise RuntimeError(f"Expected output file not found: {output_path}")

    return output_path


def compile_to_docx(source_path: Path) -> Path:
    """Compile a quarto source file to MS Word format.

    This function is maintained for backward compatibility.
    Use compile_quarto() for new code.

    Args:
        source_path: Path to the .qmd source file

    Returns:
        Path to the generated .docx file

    Raises:
        RuntimeError: If quarto is not installed or compilation fails
    """
    return compile_quarto(source_path, "docx")
