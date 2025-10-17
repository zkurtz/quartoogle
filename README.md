# quartoogle

*Pronounced "kor-TOO-gul"*

Compile your analytical reports directly to google drive. Powered by [quarto](https://quarto.org/) and the [Google Drive API](https://developers.google.com/drive).

Use it from the command line:

```bash
quartoogle example.qmd --folder-id "1a2b3c4d5e6f7g8h9i0j"

-----

INFO: Compiling example.qmd to pdf...
INFO: Successfully compiled to: example.pdf
INFO: Authenticating with Google Drive...
INFO: Uploading to Google Drive folder: 1a2b3c4d5e6f7g8h9i0j
INFO: Upload complete!
INFO: View your document at: https://docs.google.com/document/d/DOCUMENT_ID/edit
```

Or use it programmatically in your Python code:

```python
import quartoogle

file_id, url = quartoogle.publish("example.qmd", folder_id="1a2b3c4d5e6f7g8h9i0j")
print(f"Uploaded to: {url}")
```

How it works:
- Renders `.qmd` files to PDF format by default (or any other quarto format via the `--to` option)
- Uploads directly to the specified folder in your Google Drive (you must manually create the folder and obtain its ID from the URL)
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
4. Create a folder in Google Drive where you want to upload your documents, and note its folder ID from the URL (the folder ID is the long alphanumeric string after `/folders/` in the URL).


## Usage Examples

Basic command-line usage (PDF output by default):
```bash
quartoogle report.qmd --folder-id "1a2b3c4d5e6f7g8h9i0j"
```

Compile to MS Word format, or any other quarto-supported format:
```bash
quartoogle report.qmd --folder-id "1a2b3c4d5e6f7g8h9i0j" --to docx
```

Custom credentials file:
```bash
quartoogle report.qmd --folder-id "1a2b3c4d5e6f7g8h9i0j" --credentials path/to/credentials.json
```

Enable verbose logging (shows all debug messages and quarto output):
```bash
quartoogle report.qmd --folder-id "1a2b3c4d5e6f7g8h9i0j" -v
```

## Best practices

Output format:

- PDF is the best choice for most users who need user to be able to comment on the doc in google drive.
- HTML may be superior if view-ability (without commenting) is the main goal.
- Quarto also support MS Word format, but tends to have severe formatting issues even for moderately complex documents.

Development workflow: Do not call quartoogle for every dev iteration on your document. Instead, use tools like
- VSCode extension: Quarto -- enables live execution and preview of .qmd files.
- VSCode extension: vscode-pdf -- enables live preview of .pdf files.
