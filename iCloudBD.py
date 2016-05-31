import requests
import json
import os.path as path

print('iCloud Shared Download')

#sharedUrl = input('Paste Entire URL:')

#stream_id = sharedUrl.split('#').pop()

stream_id = 'B0VJ0DiRHJObc80'
base_url = 'https://p13-sharedstreams.icloud.com/' + stream_id + '/sharedstreams/'

url = base_url + 'webstream'
print('Getting Photo List From -> ' + url)

r = requests.post(url, data='{"streamCtag":null}')
data = r.json()
guids = [item['photoGuid'] for item in data['photos']]

chunk = 20
batches = zip(*[iter(guids)]*chunk)

for batch in batches:
    url = base_url + 'webasseturls'
    print('Getting Photo Urls From -> ' + url)
    r = requests.post(url, data='{"photoGuids":["' + '","'.join(batch) + '"]}')
    data = r.json()
    locations = data['locations']
    items = data['items']

    for key, item in items.items():
        file_name = key + '.jpeg'
        if not path.exists(file_name):
            location = item['url_location']
            host = locations[location]['hosts'][0]
            url = 'https://' + host + item['url_path']
            print('Downloading Photo -> ' + url)
            r = requests.get(url)
            with open(file_name, 'wb') as f:
                f.write(r.content)
