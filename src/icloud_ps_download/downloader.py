"""Download items from an iCloud shared photo stream to disk."""

from __future__ import annotations

import contextlib
import logging
import multiprocessing
import os
import time
from pathlib import Path

import requests

from icloud_ps_download.stream_parsing import DownloadItem

LOG = logging.getLogger(__name__)

_CHUNK_SIZE = 512 * 1024

parallel_requests_session: requests.Session | None = None


def subprocess_initializer() -> None:
    global parallel_requests_session
    parallel_requests_session = requests.session()


def download_item(item: DownloadItem, sess: requests.Session | None = None) -> bool:
    if sess is None:
        sess = parallel_requests_session or requests.session()

    file_path = Path(item.file_name)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    if file_path.exists():
        LOG.info("Already exists: %s", file_path)
        return False

    LOG.info(
        "Downloading photo %s derivative %s to %s (%s bytes)",
        item.template_namespace["photo_guid"],
        item.template_namespace["derivative_id"],
        file_path,
        item.derivative["fileSize"],
    )
    r = sess.get(item.url, stream=True)
    r.raise_for_status()

    temp_name = item.file_name + f".tmp-{time.time()}"
    try:
        with open(temp_name, "wb") as f:
            for chunk in r.iter_content(chunk_size=_CHUNK_SIZE):
                if chunk:
                    f.write(chunk)
        # Renames should be atomic
        os.rename(temp_name, item.file_name)
    finally:
        with contextlib.suppress(FileNotFoundError):
            os.unlink(temp_name)
    return True


def perform_download(download_items: list[DownloadItem], parallel: int = 1) -> None:
    if parallel > 1:
        with multiprocessing.Pool(processes=parallel, initializer=subprocess_initializer) as pool:
            for _ in pool.imap_unordered(download_item, download_items, chunksize=10):
                pass
    else:
        with requests.session() as sess:
            for item in download_items:
                download_item(item=item, sess=sess)
