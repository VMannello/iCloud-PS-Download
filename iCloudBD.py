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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('url', nargs='?')
    args = ap.parse_args()
    if not args.url:
        print('iCloud Shared Download')
        args.url = input('Paste Entire URL or stream ID: ')
    if '#' in args.url:
        stream_id = args.url.split('#').pop()
    else:
        stream_id = args.url
    if not stream_id.isalnum():
        raise ValueError('stream ID should be alphanumeric (got %s)' % stream_id)
    stream_contents = get_stream_contents(stream_id)
    download_items(stream_contents)


if __name__ == '__main__':
    main()
