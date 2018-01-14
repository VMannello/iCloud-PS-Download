import requests
import json
import argparse
import os.path as path


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


def download_items(stream_contents):
    locations = stream_contents['locations']
    for key, item in stream_contents['items'].items():
        file_name = key + '.jpeg'
        if not path.exists(file_name):
            location = item['url_location']
            host = locations[location]['hosts'][0]
            url = 'https://' + host + item['url_path']
            print('Downloading Photo -> ' + url)
            r = requests.get(url)
            with open(file_name, 'wb') as f:
                f.write(r.content)


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('url', nargs='?')
    ap.add_argument('--dump-json', help='dump stream info into this JSON file')
    ap.add_argument('--no-download', action='store_true', default=False, help='do not download actual items')
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
    if args.dump_json:
        with open(args.dump_json, 'w') as dump_file:
            json.dump(stream_contents, dump_file, sort_keys=True, indent=2)
            print('Wrote metadata to %s' % dump_file.name)
    if not args.no_download:
        download_items(stream_contents)
    else:
        print('Skipping item download (--no-download)')


if __name__ == '__main__':
    main()
