"""Quartoogle CLI - Compile quarto docs directly to Google Drive."""

import logging
import sys
from pathlib import Path

import click

from quartoogle.quarto import compile_to_docx
from quartoogle.gdrive import authenticate, upload_file

logger = logging.getLogger(__name__)


@click.command()
@click.argument('source', type=click.Path(exists=True, path_type=Path))
@click.option('--output', required=True, help='Google Drive directory name or ID where the file will be uploaded')
@click.option('--credentials', default='credentials.json', type=click.Path(path_type=Path), help='Path to Google OAuth2 credentials JSON file')
@click.option('-v', '--verbose', is_flag=True, help='Enable verbose logging')
def main(source, output, credentials, verbose):
    """Compile quarto docs directly to Google Drive."""
    # Setup logging based on verbose flag
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format='%(levelname)s: %(message)s'
    )
    
    try:
        # Validate source file extension
        if not source.suffix == '.qmd':
            logger.error(f"Source file must be a .qmd file, got: {source.suffix}")
            sys.exit(1)
        
        logger.info(f"Compiling {source} to MS Word...")
        docx_path = compile_to_docx(source)
        logger.info(f"Successfully compiled to: {docx_path}")
        
        logger.info("Authenticating with Google Drive...")
        service = authenticate(credentials)
        
        logger.info(f"Uploading to Google Drive directory: {output}")
        file_url = upload_file(service, docx_path, output)
        
        logger.info("Upload complete!")
        logger.info(f"View your document at: {file_url}")
        
    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}")
        if verbose:
            logger.exception("Full traceback:")
        sys.exit(1)


if __name__ == "__main__":
    main()
