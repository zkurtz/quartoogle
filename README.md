# quartoogle

Compile quarto docs directly to Google Drive

## Overview

Quartoogle is a command-line tool that compiles Quarto documents to MS Word format and uploads them directly to Google Drive. It provides a simple workflow for creating and sharing Word documents from Quarto source files.

## Installation

```bash
pip install -e .
```

## Prerequisites

1. **Quarto**: Install from https://quarto.org/docs/get-started/
2. **Google Cloud Project**: Set up OAuth2 credentials
   - Go to https://console.cloud.google.com/
   - Create a project or select an existing one
   - Enable the Google Drive API
   - Create OAuth2 credentials (Desktop app type)
   - Download the credentials JSON file and save it as `credentials.json`

## Usage

Basic usage:

```bash
quartoogle path/to/sourcefile.qmd --output "My Google Drive Folder"
```

With custom credentials file:

```bash
quartoogle path/to/sourcefile.qmd --output "My Folder" --credentials path/to/credentials.json
```

With verbose logging:

```bash
quartoogle path/to/sourcefile.qmd --output "My Folder" -v
```

### Arguments

- `source`: Path to the Quarto source file (.qmd)
- `--output`: Google Drive directory name where the file will be uploaded (will be created if it doesn't exist)
- `--credentials`: Path to Google OAuth2 credentials JSON file (default: credentials.json)
- `-v, --verbose`: Enable verbose logging

## How It Works

1. Compiles the Quarto source file to MS Word (.docx) format using `quarto render`
2. Authenticates with Google Drive (opens browser on first run)
3. Creates the specified folder in Google Drive if it doesn't exist
4. Uploads the compiled Word document
5. Prints a link to view the document on Google Drive

## Example

```bash
# Create a simple quarto document
echo "# Hello World\nThis is a test document." > test.qmd

# Upload to Google Drive
quartoogle test.qmd --output "Quartoogle Documents"
```

The log will conclude with something like:
```
INFO: Compiling test.qmd to MS Word...
INFO: Successfully compiled to: test.docx
INFO: Authenticating with Google Drive...
INFO: Uploading to Google Drive directory: Quartoogle Documents
INFO: Upload complete!
INFO: View your document at: https://docs.google.com/document/d/DOCUMENT_ID/edit
```

## License

MIT License - see LICENSE file for details
