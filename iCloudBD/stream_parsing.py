import os.path
from collections import namedtuple

DownloadItem = namedtuple('DownloadItem', ('file_name', 'url', 'photo', 'derivative', 'template_namespace'))


def generate_download_items(stream_contents, filename_template, all_derivatives=False):
    """Generates DownloadItem objects from a stream"""

    locations = stream_contents['locations']
    for index, photo in enumerate(stream_contents['stream_data']['photos']):
        derivatives = [dict(derivative, id=id) for (id, derivative) in photo['derivatives'].items()]
        if not all_derivatives:
            # Assume the largest derivative is the original:
            original_derivative = max(derivatives, key=lambda d: int(d['fileSize']))
            derivatives = [original_derivative]

        for derivative in derivatives:
            item_id = derivative['checksum']
            item = stream_contents['items'][item_id]
            original_filename = os.path.basename(item['url_path'].split('?')[0])
            template_namespace = {
                'stream_id': stream_contents['id'],
                'stream_name': stream_contents['stream_data']['streamName'],
                'photo_guid': photo['photoGuid'],
                'item_id': item_id,
                'photo_index': index,
                'photo_index_padded': '%05d' % index,
                'derivative_id': derivative['id'],
                'original_filename': original_filename,
                'original_extension': os.path.splitext(original_filename)[1],
            }

            file_name = filename_template.format(**template_namespace)
            host = locations[item['url_location']]['hosts'][0]
            url = 'https://' + host + item['url_path']

            yield DownloadItem(
                file_name=file_name,
                url=url,
                derivative=derivative,
                photo=photo,
                template_namespace=template_namespace,
            )
