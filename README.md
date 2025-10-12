# quartoogle

*Pronounced "quart-oo-gul"*

Compile quarto docs directly to Google Drive. Example:

```bash
quartoogle example.qmd --output "My Google Drive Folder"
```

Output:
```
INFO: Compiling example.qmd to MS Word...
INFO: Successfully compiled to: example.docx
INFO: Authenticating with Google Drive...
INFO: Uploading to Google Drive directory: My Google Drive Folder
INFO: Upload complete!
INFO: View your document at: https://docs.google.com/document/d/DOCUMENT_ID/edit
```

## Features

- **Quarto compilation** - Automatically renders `.qmd` files to MS Word format
- **Google Drive integration** - Uploads directly to your Google Drive
- **OAuth2 authentication** - Secure authentication with token caching
- **Automatic folder creation** - Creates target folders if they don't exist
- **Verbose logging** - Optional `-v` flag for detailed output

## Installation

```bash
pip install -e .
```

## Prerequisites

1. **Quarto** - Install from https://quarto.org/docs/get-started/
2. **Google OAuth2 credentials**:
   - Go to https://console.cloud.google.com/
   - Create a project and enable the Google Drive API
   - Create OAuth2 credentials (Desktop app type)
   - Download as `credentials.json`

## Usage Examples

Basic usage:
```bash
quartoogle report.qmd --output "Reports"
```

Custom credentials file:
```bash
quartoogle report.qmd --output "Reports" --credentials path/to/credentials.json
```

Verbose mode:
```bash
quartoogle report.qmd --output "Reports" -v
```
