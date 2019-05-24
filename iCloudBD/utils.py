def do_batch(value, batch_size):
    tmp = []
    for item in value:
        if len(tmp) == batch_size:
            yield tmp
            tmp = []
        tmp.append(item)
    if tmp:
        yield tmp
