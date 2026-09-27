from __future__ import annotations

from icloud_ps_download.stream_parsing import DownloadItem, generate_download_items


SAMPLE_STREAM = {
    "id": "teststream",
    "stream_data": {
        "streamName": "My Stream",
        "photos": [
            {
                "photoGuid": "guid-1",
                "derivatives": {
                    "1024": {"checksum": "chk-1", "fileSize": "100", "id": "1024"},
                    "2048": {"checksum": "chk-2", "fileSize": "500", "id": "2048"},
                },
            },
        ],
    },
    "locations": {
        "loc-1": {"hosts": ["p123-sharedstreams.icloud.com"]},
    },
    "items": {
        "chk-1": {"url_location": "loc-1", "url_path": "/path/1/photo.jpg?token=abc"},
        "chk-2": {"url_location": "loc-1", "url_path": "/path/2/photo_large.jpg?token=def"},
    },
}


def test_generate_download_items_picks_largest_derivative():
    items = list(generate_download_items(SAMPLE_STREAM, filename_template="{original_filename}"))
    assert len(items) == 1
    item = items[0]
    assert item.derivative["id"] == "2048"
    assert item.file_name == "photo_large.jpg"
    assert item.url == "https://p123-sharedstreams.icloud.com/path/2/photo_large.jpg?token=def"


def test_generate_download_items_all_derivatives():
    items = list(
        generate_download_items(
            SAMPLE_STREAM, filename_template="{derivative_id}_{original_filename}", all_derivatives=True
        )
    )
    assert len(items) == 2
    derivative_ids = {item.derivative["id"] for item in items}
    assert derivative_ids == {"1024", "2048"}


def test_generate_download_items_template_namespace():
    items = list(
        generate_download_items(SAMPLE_STREAM, filename_template="{stream_id}/{photo_index_padded}_{original_filename}")
    )
    assert len(items) == 1
    item = items[0]
    assert item.file_name == "teststream/00000_photo_large.jpg"
    assert item.template_namespace["stream_name"] == "My Stream"
    assert item.template_namespace["photo_guid"] == "guid-1"
    assert item.template_namespace["photo_index"] == 0


def test_generate_download_items_missing_item(capsys):
    stream = {
        "id": "s",
        "stream_data": {
            "streamName": "S",
            "photos": [{"photoGuid": "g", "derivatives": {"1": {"checksum": "missing", "fileSize": "10", "id": "1"}}}],
        },
        "locations": {},
        "items": {},
    }
    items = list(generate_download_items(stream, filename_template="{original_filename}"))
    assert items == []
    # Warning is logged, not printed
    assert capsys.readouterr().out == ""


def test_download_item_is_namedtuple():
    assert DownloadItem._fields == (
        "file_name",
        "url",
        "photo",
        "derivative",
        "template_namespace",
    )
