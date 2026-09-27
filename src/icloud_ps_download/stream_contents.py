"""Fetch stream contents from the iCloud shared photo stream API."""

from __future__ import annotations

import json
import logging
import random
import string
import time
from typing import Any

import requests

from icloud_ps_download.utils import do_batch

LOG = logging.getLogger(__name__)

DEFAULT_MME_HOST = "p13-sharedstreams.icloud.com"
_REQUEST_TIMEOUT = 30
_BATCH_SIZE = 20
_RANDOM = random.SystemRandom()


def get_stream_contents(stream_id: str, mme_host: str = DEFAULT_MME_HOST) -> dict[str, Any]:
    """Get available assets for a given stream ID."""
    base_url = f"https://{mme_host}/{stream_id}/sharedstreams/"
    url = base_url + "webstream"
    LOG.info("Getting photo list...")
    r = requests.post(url, data=json.dumps({"streamCtag": None}), timeout=_REQUEST_TIMEOUT)
    stream_data = r.json()

    if "X-Apple-MMe-Host" in stream_data:
        mme_host = stream_data["X-Apple-MMe-Host"]
        LOG.info("iCloud says we should try again at %s", mme_host)
        return get_stream_contents(stream_id, mme_host=mme_host)

    guids = [item["photoGuid"] for item in stream_data["photos"]]
    LOG.info("%d items in stream.", len(guids))
    batches = list(do_batch(guids, batch_size=_BATCH_SIZE))
    locations: dict[str, Any] = {}
    items: dict[str, Any] = {}
    for i, batch in enumerate(batches, 1):
        url = base_url + "webasseturls"
        LOG.info("Getting photo URLs (%d/%d)...", i, len(batches))
        r = requests.post(url, data=json.dumps({"photoGuids": list(batch)}), timeout=_REQUEST_TIMEOUT)
        batch_data = r.json()
        locations.update(batch_data.get("locations", {}))
        items.update(batch_data.get("items", {}))

        # Sleep for a while to avoid 509 throttling errors
        time.sleep(_RANDOM.uniform(0.5, 1.2))

    return {
        "id": stream_id,
        "stream_data": stream_data,
        "locations": locations,
        "items": items,
    }


def get_stream_id(url: str) -> str:
    """Extract the stream ID from a shared album URL or return the input if already an ID."""
    stream_id = url.split("#").pop() if "#" in url else url
    # New-style stream IDs are tokens that may also contain '-' and '_'
    if not stream_id or set(stream_id) - set(string.ascii_letters + string.digits + "-_"):
        raise ValueError(f"stream ID contains unexpected characters (got {stream_id})")
    return stream_id
