# Integration Testing Guide

This document describes how to perform integration testing of quartoogle with real Quarto and Google Drive.

## Prerequisites

1. Install Quarto from https://quarto.org/docs/get-started/
2. Set up Google Cloud OAuth2 credentials (see README.md)
3. Install quartoogle: `pip install -e .`

## Testing Steps

### 1. Test Quarto Compilation

```bash
# Navigate to the examples directory
cd examples

# Manually test quarto compilation
quarto render example.qmd --to docx

# Verify example.docx was created
ls -l example.docx
```

### 2. Test CLI with Dry Run (without Google Drive)

```bash
# Test CLI help
quartoogle --help

# Test with missing file (should fail gracefully)
quartoogle nonexistent.qmd --output test

# Test with wrong file type (should fail gracefully)
echo "test" > test.txt
quartoogle test.txt --output test
```

### 3. Test Google Drive Integration

**Important**: This requires valid Google OAuth2 credentials.

```bash
# Place your credentials.json in the root directory
# Then run:
quartoogle examples/example.qmd --output "Quartoogle Test"

# Expected output:
# INFO: Compiling examples/example.qmd to MS Word...
# INFO: Successfully compiled to: examples/example.docx
# INFO: Authenticating with Google Drive...
# INFO: Opening browser for authentication... (first time only)
# INFO: Uploading to Google Drive directory: Quartoogle Test
# INFO: Upload complete!
# INFO: View your document at: https://docs.google.com/document/d/...
```

### 4. Test with Verbose Logging

```bash
quartoogle examples/example.qmd --output "Quartoogle Test" -v
```

### 5. Test with Custom Credentials Path

```bash
quartoogle examples/example.qmd --output "Test Folder" --credentials /path/to/credentials.json
```

## Automated Tests

Run the test suite:

```bash
pytest tests/ -v
```

Run with coverage:

```bash
pytest tests/ --cov=quartoogle --cov-report=html
```

## Cleanup

After testing, you can remove:
- `examples/example.docx` (compiled output)
- `token.json` (cached OAuth token)
- Any test folders created in Google Drive

## Troubleshooting

### Quarto Not Found

If you get "Quarto is not installed":
- Install Quarto from https://quarto.org/docs/get-started/
- Ensure `quarto` is in your PATH
- Test with `quarto --version`

### Google Authentication Fails

If authentication fails:
- Verify credentials.json is valid
- Delete token.json and try again
- Check Google Cloud Console API settings
- Ensure Google Drive API is enabled

### Upload Fails

If upload fails:
- Check internet connectivity
- Verify credentials have Drive API scope
- Check folder permissions
- Try with verbose flag (-v) for details
