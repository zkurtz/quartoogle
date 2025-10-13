"""Quartoogle CLI - Compile quarto docs directly to Google Drive."""

import logging
import sys
from pathlib import Path

import click

from quartoogle import constants
from quartoogle.api import publish

logger = logging.getLogger(__name__)


@click.command()
@click.argument("source", type=click.Path(exists=True, path_type=Path))
@click.option("--folder-id", required=True, help="Google Drive folder ID where the file will be uploaded")
@click.option(
    "--to",
    "output_format",
    default="pdf",
    help="Output format (e.g., pdf, docx, html). Default is pdf.",
)
@click.option(
    "--credentials",
    default=constants.CREDS_PATH,
    type=click.Path(path_type=Path),
    help="Path to Google OAuth2 credentials JSON file",
)
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose logging")
def main(source: Path, folder_id: str, output_format: str, credentials: Path, verbose: bool) -> None:
    """Compile quarto docs directly to Google Drive."""
    # Setup logging based on verbose flag
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO, format="%(levelname)s: %(message)s")

    try:
        # Use the publish API function
        publish(source, folder_id, output_format, credentials)

    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user")
        sys.exit(1)
    except ValueError as e:
        logger.error(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}")
        if verbose:
            logger.exception("Full traceback:")
        sys.exit(1)


if __name__ == "__main__":
    main()
