"""Quarto compilation utilities."""

import logging
from pathlib import Path

from quarto import render

logger = logging.getLogger(__name__)


def compile_to_docx(source_path: Path) -> Path:
    """Compile a quarto source file to MS Word format.

    Args:
        source_path: Path to the .qmd source file

    Returns:
        Path to the generated .docx file

    Raises:
        RuntimeError: If quarto is not installed or compilation fails
    """
    logger.debug(f"Rendering {source_path} to docx")
    render(str(source_path), output_format="docx")

    # Determine output path (quarto creates .docx next to source)
    docx_path = source_path.with_suffix(".docx")

    if not docx_path.exists():
        raise RuntimeError(f"Expected output file not found: {docx_path}")

    return docx_path
