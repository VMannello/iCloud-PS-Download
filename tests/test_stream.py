from __future__ import annotations

from icloud_ps_download.stream_contents import get_stream_id
from icloud_ps_download.utils import do_batch

import pytest


@pytest.mark.parametrize(
    "url, expected",
    [
        ("https://www.icloud.com/sharedalbum/#D2Lv3syhlfFLhmu", "D2Lv3syhlfFLhmu"),
        (
            "https://www.icloud.com/sharedalbum/#D2Lv3syhlfFLhmu_t83TinsiwcwCAEQARogxS1J34aNA3Ea7Ic-tRhUGMYkjjEe4bPseDpNZiXt7Q4",
            "D2Lv3syhlfFLhmu_t83TinsiwcwCAEQARogxS1J34aNA3Ea7Ic-tRhUGMYkjjEe4bPseDpNZiXt7Q4",
        ),
        ("Abc123", "Abc123"),
    ],
)
def test_get_stream_id_valid(url, expected):
    assert get_stream_id(url) == expected


@pytest.mark.parametrize(
    "url",
    [
        "https://www.icloud.com/sharedalbum/#bad/id",
        "https://www.icloud.com/sharedalbum/#has spaces",
        "https://www.icloud.com/sharedalbum/#has!special",
    ],
)
def test_get_stream_id_invalid(url):
    with pytest.raises(ValueError, match="unexpected characters"):
        get_stream_id(url)


def test_get_stream_id_empty_fragment():
    with pytest.raises(ValueError, match="unexpected characters"):
        get_stream_id("https://www.icloud.com/sharedalbum/#")


def test_do_batch_exact():
    assert list(do_batch([1, 2, 3, 4, 6], batch_size=2)) == [[1, 2], [3, 4], [6]]


def test_do_batch_larger_than_input():
    assert list(do_batch([1, 2], batch_size=5)) == [[1, 2]]


def test_do_batch_empty():
    assert list(do_batch([], batch_size=3)) == []


def test_do_batch_single_batch():
    assert list(do_batch(range(3), batch_size=3)) == [[0, 1, 2]]
