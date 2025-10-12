# quartoogle

*Pronounced "kor-TOO-gul"*

Compile quarto docs directly to Google Drive. Example:

```bash
quartoogle example.qmd --output "My Google Drive Folder"

-----

INFO: Compiling example.qmd to MS Word...
INFO: Successfully compiled to: example.docx
INFO: Authenticating with Google Drive...
INFO: Uploading to Google Drive directory: My Google Drive Folder
INFO: Upload complete!
INFO: View your document at: https://docs.google.com/document/d/DOCUMENT_ID/edit
```

How it works:
- Renders `.qmd` files to MS Word format
- Uploads directly to the specified folder in your Google Drive, creating the folder if it does not exist
- Uses OAuth2 authentication (Secure authentication with token caching)


## Set up

1. Install quarto from https://quarto.org/docs/get-started/
2. Setup google OAuth2 credentials:
   - Go to https://console.cloud.google.com/
   - Create a project and enable the Google Drive API
   - Create OAuth2 credentials (Desktop app type)
   - Download as `credentials.json`
3. Install quartoogle: We're [on pypi](https://pypi.org/project/quartoogle/), so `uv add quartoogle`. If working directly on this repo, consider using the [simplest-possible virtual environment](https://gist.github.com/zkurtz/4c61572b03e667a7596a607706463543).


## Usage Examples

Basic usage:
```bash
quartoogle report.qmd --output "Reports"
```

Verbose mode:
```bash
quartoogle report.qmd --output "Reports" -v
```

Custom credentials file:
```bash
quartoogle report.qmd --output "Reports" --credentials path/to/credentials.json
```

