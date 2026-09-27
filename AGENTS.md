# Agent Guidelines for iCloud-PS-Download

Python CLI tool for downloading photos from iCloud shared photo streams.

## General

- Source layout: `src/icloud_ps_download/` package, tests in `tests/`
- Uses `uv` for dependency management and `uv_build` as the build backend
- Hook manager: `prek` (pre-commit replacement); hooks: ruff (check + format), ty, pyupgrade

## Python Version

- **Minimum**: Python 3.13
- **CI**: Python 3.14

## Development Commands

### Environment Setup
```bash
uv sync
prek install
```

### Testing
```bash
pytest                          # All tests
pytest tests/test_stream.py     # Single file
pytest -vv                      # Verbose
pytest --cov=src                # With coverage
```

### Code Quality
```bash
ruff check --fix src tests      # Linter (auto-fixes)
ruff format src tests           # Format
ty check                        # Type checker
prek run -a                    # Run all hooks
```

### Running
```bash
uv run icloud-ps-download --help
uv run icloud-ps-download "https://www.icloud.com/sharedalbum/#<stream-id>"
```

## Code Style

### Imports
- Always at the top of each Python file
- Single-line imports only (enforced by ruff isort)
- Three groups: stdlib, third-party, local
- Alphabetize within groups

### Formatting
- Line length: 120 chars
- Linting/formatting: ruff
- LF endings, no trailing whitespace

### Type Hints
- Use consistently for signatures and returns
- Union with `|`: `str | None`, `Path | None`

### Logging
- `LOG = logging.getLogger(__name__)` per module
- Use `LOG.info()`, `LOG.warning()`, `LOG.error()` instead of `print()`

### Naming
- Variables/functions/modules: `snake_case`
- Classes: `TitleCase`
- Constants: `UPPER_SNAKE_CASE`
