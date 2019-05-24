import os.path

import requests

parallel_requests_session = None


def subprocess_initializer():
    global parallel_requests_session
    parallel_requests_session = requests.session()


def download_item(item, sess=None):
    if not sess:
        sess = parallel_requests_session

    os.makedirs(os.path.dirname(item.file_name), exist_ok=True)
    if os.path.exists(item.file_name):
        print('Already exists: %s' % item.file_name)
        return False

    print('Downloading photo %s derivative %s to %s (%s bytes)' % (
        item.template_namespace['photo_guid'],
        item.template_namespace['derivative_id'],
        item.file_name,
        item.derivative['fileSize'],
    ))
    r = sess.get(item.url, stream=True)
    r.raise_for_status()
    with open(item.file_name, 'wb') as f:
        for chunk in r.iter_content(chunk_size=512 * 1024):
            if chunk:
                f.write(chunk)
    return r


def perform_download(download_items, parallel=0):
    if parallel > 1:
        import multiprocessing
        with multiprocessing.Pool(processes=parallel, initializer=subprocess_initializer) as p:
            for result in p.imap_unordered(download_item, download_items, chunksize=10):
                pass
    else:
        with requests.session() as sess:
            for item in download_item:
                download_item(item=item, sess=sess)
