# iCloud-PS-Download

Download all photos and videos from a public iCloud shared photo stream (shared album), given the album's `https://www.icloud.com/sharedalbum/#<stream-id>` URL. No Apple ID login is required for publicly shared albums.

## Installation

### As a standalone tool (recommended)

Requires [uv](https://docs.astral.sh/uv/) (or Python >= 3.13 with `pipx`).

Install the latest release directly from GitHub:

```bash
uv tool install git+https://github.com/VMannello/iCloud-PS-Download
```

Or with pipx:

```bash
pipx install git+https://github.com/VMannello/iCloud-PS-Download
```

This provides the `icloud-ps-download` command on your `PATH`, which you can run from any directory.

### From source (for development)

```bash
git clone https://github.com/VMannello/iCloud-PS-Download
cd iCloud-PS-Download
uv sync
prek install
```

When working from a source checkout, prefix all commands below with `uv run`, e.g.:

```bash
uv run icloud-ps-download --help
```

## Usage

Get the shared album URL from the album owner (or from the iCloud web UI when opening the shared album). Then run:

```bash
icloud-ps-download "https://www.icloud.com/sharedalbum/#<stream-id>"
```

Photos and videos are downloaded to `./<stream-id>/` by default; use `--download-filename-template` to change this (see below).

### Options

```
url                                    iCloud shared album URL
--dump-json PATH                       Dump stream metadata to this JSON file
--no-download                          Do not download actual items
--download-filename-template TEMPLATE  File download name template (default: ./{stream_id}/{original_filename})
--all-derivatives                      Download all derivatives (not just assumed original)
--parallel N                           How many downloads to do in parallel (default: 1)
```

### Filename template placeholders

`{stream_id}`, `{stream_name}`, `{photo_guid}`, `{item_id}`, `{photo_index}`,
`{photo_index_padded}`, `{derivative_id}`, `{original_filename}`, `{original_extension}`

### Examples

Download everything into the default directory:

```bash
icloud-ps-download "https://www.icloud.com/sharedalbum/#B0X5YnKs9mGfspx"
```

Download four files in parallel, keeping the album name and an index in the file names:

```bash
icloud-ps-download \
  --parallel 4 \
  --download-filename-template "./{stream_name}/{photo_index_padded}_{original_filename}" \
  "https://www.icloud.com/sharedalbum/#B0X5YnKs9mGfspx"
```

Only dump the album metadata to JSON, without downloading:

```bash
icloud-ps-download --no-download --dump-json album.json "https://www.icloud.com/sharedalbum/#B0X5YnKs9mGfspx"
```

## Requirements

- Python >= 3.13
- For publicly shared albums no Apple ID or password is needed.

## Development

```bash
uv sync                    # Install dependencies
prek install               # Install git hooks (via prek, a pre-commit replacement)
pytest                     # Run tests
ruff check --fix src tests # Lint
ruff format src tests      # Format
ty check                   # Type check
```
