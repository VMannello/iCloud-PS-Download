import os.path


def download_item(sess, item):
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
