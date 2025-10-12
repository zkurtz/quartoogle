"""Quartoogle CLI - Compile quarto docs directly to Google Drive."""

import argparse
import logging
import sys
from pathlib import Path

from quartoogle.quarto import compile_to_docx
from quartoogle.gdrive import authenticate, upload_file

logger = logging.getLogger(__name__)


def main():
    """Main entry point for the quartoogle CLI."""
    parser = argparse.ArgumentParser(
        description="Compile quarto docs directly to Google Drive"
    )
    parser.add_argument(
        "source",
        type=str,
        help="Path to the quarto source file (.qmd)"
    )
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Google Drive directory name or ID where the file will be uploaded"
    )
    parser.add_argument(
        "--credentials",
        type=str,
        default="credentials.json",
        help="Path to Google OAuth2 credentials JSON file (default: credentials.json)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(levelname)s: %(message)s'
    )
    
    try:
        # Validate source file exists
        source_path = Path(args.source)
        if not source_path.exists():
            logger.error(f"Source file not found: {args.source}")
            sys.exit(1)
        
        if not source_path.suffix == '.qmd':
            logger.error(f"Source file must be a .qmd file, got: {source_path.suffix}")
            sys.exit(1)
        
        logger.info(f"Compiling {args.source} to MS Word...")
        docx_path = compile_to_docx(source_path)
        logger.info(f"Successfully compiled to: {docx_path}")
        
        logger.info("Authenticating with Google Drive...")
        credentials_path = Path(args.credentials)
        service = authenticate(credentials_path)
        
        logger.info(f"Uploading to Google Drive directory: {args.output}")
        file_url = upload_file(service, docx_path, args.output)
        
        logger.info("Upload complete!")
        logger.info(f"View your document at: {file_url}")
        
    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}")
        if args.verbose:
            logger.exception("Full traceback:")
        sys.exit(1)


if __name__ == "__main__":
    main()
