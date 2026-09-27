"""Download photos from iCloud shared photo streams."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from icloud_ps_download.downloader import perform_download
from icloud_ps_download.stream_contents import get_stream_contents, get_stream_id
from icloud_ps_download.stream_parsing import generate_download_items

LOG = logging.getLogger(__name__)

DEFAULT_TEMPLATE = "./{stream_id}/{original_filename}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="icloud-ps-download",
        description="Download photos from an iCloud shared photo stream.",
    )
    parser.add_argument("url", help="iCloud shared album URL (e.g. https://www.icloud.com/sharedalbum/#<id>)")
    parser.add_argument("--dump-json", type=Path, help="Dump stream metadata to this JSON file")
    parser.add_argument(
        "--no-download",
        action="store_true",
        default=False,
        help="Do not download actual items",
    )
    parser.add_argument(
        "--download-filename-template",
        default=DEFAULT_TEMPLATE,
        help=f'File download name template (use {{}} placeholders)\nDefault "{DEFAULT_TEMPLATE}"',
    )
    parser.add_argument(
        "--all-derivatives",
        action="store_true",
        help="Download all derivatives (not just assumed original) (be careful with the filename template!)",
    )
    parser.add_argument(
        "--parallel",
        type=int,
        default=1,
        help="How many downloads to do in parallel (defaults to 1)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    stream_id = get_stream_id(url=args.url)
    stream_contents = get_stream_contents(stream_id)

    if args.dump_json:
        with args.dump_json.open("w") as dump_file:
            json.dump(stream_contents, dump_file, sort_keys=True, indent=2)
            LOG.info("Wrote metadata to %s", args.dump_json)

    if not args.no_download:
        download_items = list(
            generate_download_items(
                stream_contents,
                filename_template=args.download_filename_template,
                all_derivatives=args.all_derivatives,
            )
        )
        perform_download(download_items, parallel=args.parallel)
    else:
        LOG.info("Skipping item download (--no-download)")
