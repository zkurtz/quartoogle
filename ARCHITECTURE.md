# Architecture

This document describes the architecture and design decisions of quartoogle.

## Overview

Quartoogle is a Python CLI tool that bridges Quarto and Google Drive, providing a seamless workflow for publishing Quarto documents to Google Drive.

## Components

### 1. CLI Module (`cli.py`)

**Responsibility**: Command-line interface and orchestration

- Parses command-line arguments using `argparse`
- Validates input files and arguments
- Orchestrates the workflow:
  1. Compile Quarto → DOCX
  2. Authenticate with Google Drive
  3. Upload to Google Drive
- Provides user feedback through logging
- Handles errors gracefully

**Key Functions**:
- `main()`: Entry point for the CLI

### 2. Quarto Module (`quarto.py`)

**Responsibility**: Quarto document compilation

- Checks if Quarto is installed
- Runs `quarto render` to compile `.qmd` files to `.docx` format
- Validates that the output file was created
- Provides detailed error messages

**Key Functions**:
- `compile_to_docx(source_path)`: Compiles a Quarto source file to MS Word

**Design Decisions**:
- Uses subprocess to run Quarto CLI (no Python Quarto API available)
- 5-minute timeout for compilation to handle large documents
- Returns Path object for type safety

### 3. Google Drive Module (`gdrive.py`)

**Responsibility**: Google Drive API integration

**Key Functions**:
- `authenticate(credentials_path)`: OAuth2 authentication with token caching
- `find_or_create_folder(service, folder_name)`: Finds or creates a folder by name
- `upload_file(service, file_path, destination)`: Uploads a file to Google Drive

**Design Decisions**:

1. **Token Caching**: Saves OAuth2 tokens to `token.json` to avoid repeated authentication
2. **Automatic Folder Creation**: Creates folders if they don't exist
3. **Flexible Folder Specification**: Accepts either folder name or ID
4. **Proper MIME Types**: Uses correct MIME type for DOCX files
5. **Web View Links**: Returns Google Docs URLs for easy sharing

### 4. Package Structure

```
quartoogle/
├── src/quartoogle/          # Source code
│   ├── __init__.py         # Package initialization
│   ├── cli.py              # CLI entry point
│   ├── quarto.py           # Quarto compilation
│   └── gdrive.py           # Google Drive API
├── tests/                   # Test suite
│   ├── test_cli.py         # CLI tests
│   ├── test_quarto.py      # Quarto tests
│   └── test_gdrive.py      # Google Drive tests
├── examples/                # Example documents
│   └── example.qmd         # Sample Quarto file
├── pyproject.toml          # Package configuration
├── README.md               # User documentation
├── TESTING.md              # Testing guide
└── ARCHITECTURE.md         # This file
```

## Workflow

```
User runs: quartoogle source.qmd --output "My Folder"
            ↓
    CLI validates arguments
            ↓
    Quarto compiles .qmd → .docx
            ↓
    Google Drive authenticates
            ↓
    Google Drive finds/creates folder
            ↓
    Google Drive uploads .docx
            ↓
    CLI displays link to document
```

## Error Handling

Each module handles its own errors and raises informative `RuntimeError` exceptions:

1. **Quarto Module**:
   - Missing Quarto installation
   - Compilation failures
   - Missing output files

2. **Google Drive Module**:
   - Missing credentials
   - Authentication failures
   - API errors (HttpError)
   - Upload failures

3. **CLI Module**:
   - Missing/invalid source files
   - Invalid file extensions
   - Catches all errors and provides user-friendly messages
   - Verbose mode shows full tracebacks

## Dependencies

### Required
- `google-auth`: Google authentication
- `google-auth-oauthlib`: OAuth2 flow
- `google-auth-httplib2`: HTTP transport
- `google-api-python-client`: Google Drive API client

### External
- Quarto CLI (must be installed separately)

### Development
- `pytest`: Testing framework
- `pytest-cov`: Coverage reporting

## Design Principles

1. **Minimal Changes**: Keep code focused on core functionality
2. **Error Messages**: Provide helpful error messages with actionable guidance
3. **Type Safety**: Use Path objects instead of strings where appropriate
4. **Testing**: Comprehensive unit tests with mocking
5. **Logging**: Clear progress logging with optional verbose mode
6. **User Experience**: Simple CLI with sensible defaults
7. **Security**: Don't commit credentials or tokens to git

## Future Enhancements

Possible future improvements:

1. **Batch Processing**: Upload multiple files at once
2. **Watch Mode**: Automatically recompile and upload on changes
3. **Custom Formats**: Support other output formats (PDF, HTML)
4. **Folder Hierarchies**: Support nested folder paths
5. **Sharing Settings**: Configure document sharing/permissions
6. **Progress Bars**: Show upload progress for large files
7. **Config Files**: Support `.quartoogle.toml` for default settings
8. **Google Docs Conversion**: Convert to native Google Docs format
