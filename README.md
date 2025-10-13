# quartoogle

*Pronounced "kor-TOO-gul"*

Compile your analytical reports directly to google docs, enabling your readers to comment directly on your work. Powered by [quarto](https://quarto.org/) and the [Google Drive API](https://developers.google.com/drive). Example:

```bash
quartoogle example.qmd --output "quartoogle-demo"

-----

INFO: Compiling example.qmd to pdf...
INFO: Successfully compiled to: example.pdf
INFO: Authenticating with Google Drive...
INFO: Uploading to Google Drive directory: My Google Drive Folder
INFO: Upload complete!
INFO: View your document at: https://docs.google.com/document/d/DOCUMENT_ID/edit
```

How it works:
- Renders `.qmd` files to PDF format by default (or any other quarto format via the `--to` option)
- Uploads directly to the specified folder in your Google Drive, creating the folder if it does not exist
- Automatically adds a timestamp to uploaded filenames (format: `[basename]_YYYY-MM-DD_HH-MM[extension]`) to help distinguish between multiple versions
- Uses OAuth2 authentication (Secure authentication with token caching)


## Set up

1. Install quarto from https://quarto.org/docs/get-started/
2. Setup google OAuth2 credentials:
   - Go to https://console.cloud.google.com/
   - Create a project and enable the Google Drive API
   - Create OAuth2 credentials (Desktop app type)
   - Download as `credentials.json` to `~/.config/google/drive/credentials.json` (create directories as needed). Note that if you use a different path, you must specify it in the `--credentials` argument when running `quartoogle` (see example below).
3. Install quartoogle: We're [on pypi](https://pypi.org/project/quartoogle/), so `uv add quartoogle`. If working directly on this repo, consider using the [simplest-possible virtual environment](https://gist.github.com/zkurtz/4c61572b03e667a7596a607706463543).


## Usage Examples

Basic usage (PDF output by default):
```bash
quartoogle report.qmd --output "Reports"
```

Compile to MS Word format:
```bash
quartoogle report.qmd --output "Reports" --to docx
```

Compile to HTML format:
```bash
quartoogle report.qmd --output "Reports" --to html
```

Verbose mode:
```bash
quartoogle report.qmd --output "Reports" -v
```

Custom credentials file:
```bash
quartoogle report.qmd --output "Reports" --credentials path/to/credentials.json
```

