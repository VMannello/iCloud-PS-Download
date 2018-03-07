import requests
import json
import argparse
import tempfile
import os.path
from shutil import copyfile

def get_stream_contents(stream_id):
    base_url = 'https://p13-sharedstreams.icloud.com/' + stream_id + '/sharedstreams/'
    url = base_url + 'webstream'
    print('Getting photo list...')
    r = requests.post(url, data=json.dumps({"streamCtag": None}))
    stream_data = r.json()
    guids = [item['photoGuid'] for item in stream_data['photos']]
    print('%d items in stream.' % len(guids))
    chunk = 20
    batches = list(zip(*[iter(guids)] * chunk))
    locations = {}
    items = {}
    for i, batch in enumerate(batches, 1):
        url = base_url + 'webasseturls'
        print('Getting photo URLs (%d/%d)...' % (i, len(batches)))
        r = requests.post(url, data=json.dumps({"photoGuids": list(batch)}))
        batch_data = r.json()
        locations.update(batch_data.get('locations', {}))
        items.update(batch_data.get('items', {}))

    return {
        'stream_data': stream_data,
        'locations': locations,
        'items': items,
    }


def download_items(stream_contents, filename_template, all_derivatives=False):
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
            os.makedirs(os.path.dirname(file_name), exist_ok=True)
            if os.path.exists(file_name):
                print('Already exists: %s' % file_name)
                continue
            location = item['url_location']
            host = locations[location]['hosts'][0]
            url = 'https://' + host + item['url_path']
            print('Downloading photo %s derivative %s to %s (%s bytes)' % (
                template_namespace['photo_guid'],
                template_namespace['derivative_id'],
                file_name,
                derivative['fileSize'],
            ))
            r = requests.get(url, stream=True)
            r.raise_for_status()
            tf = tempfile.NamedTemporaryFile()
            with open(tf.name, 'wb') as f:
                for chunk in r.iter_content(chunk_size=512 * 1024):
                    if chunk:
                        f.write(chunk)
            copyfile(tf.name, file_name)


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('url', nargs='?')
    ap.add_argument('--dump-json', help='dump stream info into this JSON file')
    ap.add_argument('--no-download', action='store_true', default=False, help='do not download actual items')
    ap.add_argument(
        '--download-filename-template',
        default='./{stream_id}/{original_filename}',
        help='File download name template (use {} placeholders)\nDefault "%(default)s"',
    )
    ap.add_argument(
        '--all-derivatives',
        action='store_true',
        help='download all derivatives (not just assumed original) (be careful with the filename template!)',
    )
    args = ap.parse_args()
    if not args.url:
        print('iCloud Shared Download')
        args.url = input('Paste Entire URL or stream ID: ')
    return args


def main():
    args = parse_args()
    if '#' in args.url:
        stream_id = args.url.split('#').pop()
    else:
        stream_id = args.url
    if not stream_id.isalnum():
        raise ValueError('stream ID should be alphanumeric (got %s)' % stream_id)
    stream_contents = get_stream_contents(stream_id)
    stream_contents['id'] = stream_id
    if args.dump_json:
        with open(args.dump_json, 'w') as dump_file:
            json.dump(stream_contents, dump_file, sort_keys=True, indent=2)
            print('Wrote metadata to %s' % dump_file.name)
    if not args.no_download:
        download_items(
            stream_contents,
            filename_template=args.download_filename_template,
            all_derivatives=args.all_derivatives,
        )
    else:
        print('Skipping item download (--no-download)')


if __name__ == '__main__':
    main()
