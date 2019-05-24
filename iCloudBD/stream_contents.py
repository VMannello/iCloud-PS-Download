import json
import random
import time

import requests


def get_stream_contents(stream_id, mme_host='p13-sharedstreams.icloud.com'):
    """Gets available assets"""
    base_url = 'https://' + mme_host + '/' + stream_id + '/sharedstreams/'
    url = base_url + 'webstream'
    print('Getting photo list...')
    r = requests.post(url, data=json.dumps({"streamCtag": None}))
    stream_data = r.json()

    if 'X-Apple-MMe-Host' in stream_data:
        mme_host = stream_data['X-Apple-MMe-Host']
        print('iCloud says we should try again at %s' % mme_host)
        return get_stream_contents(stream_id, mme_host=mme_host)

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

        # Sleep for a while to avoid 509 throttling errors
        time.sleep(random.uniform(.5, 1.2))

    return {
        'stream_data': stream_data,
        'locations': locations,
        'items': items,
    }
