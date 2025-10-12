"""Quarto compilation utilities."""

import logging
import subprocess
from pathlib import Path

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
    # Check if quarto is installed
    try:
        result = subprocess.run(["quarto", "check"], capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            logger.warning("Quarto check returned non-zero status")
    except FileNotFoundError:
        raise RuntimeError("Quarto is not installed. Please install quarto from https://quarto.org/docs/get-started/")
    except subprocess.TimeoutExpired:
        logger.warning("Quarto check timed out, continuing anyway")

    # Compile the source file to docx
    logger.debug(f"Running: quarto render {source_path} --to docx")
    try:
        result = subprocess.run(
            ["quarto", "render", str(source_path), "--to", "docx"],
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutes timeout
        )

        if result.returncode != 0:
            error_msg = f"Quarto compilation failed:\n{result.stderr}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        logger.debug(f"Quarto output:\n{result.stdout}")

    except subprocess.TimeoutExpired:
        raise RuntimeError("Quarto compilation timed out (>5 minutes)")
    except Exception as e:
        raise RuntimeError(f"Failed to run quarto: {e}")

    # Determine output path (quarto creates .docx next to source)
    docx_path = source_path.with_suffix(".docx")

    if not docx_path.exists():
        raise RuntimeError(f"Expected output file not found: {docx_path}")

    return docx_path
