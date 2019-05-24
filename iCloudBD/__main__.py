import argparse
import json

from iCloudBD.downloader import perform_download
from iCloudBD.stream_contents import get_stream_contents
from iCloudBD.stream_parsing import generate_download_items


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('url')
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
    ap.add_argument(
        '--parallel',
        type=int,
        default=1,
        help='how many downloads to do in parallel (defaults to 1)',
    )
    args = ap.parse_args()
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
        download_items = list(generate_download_items(
            stream_contents,
            filename_template=args.download_filename_template,
            all_derivatives=args.all_derivatives,
        ))
        perform_download(download_items, parallel=args.parallel)
    else:
        print('Skipping item download (--no-download)')


if __name__ == '__main__':
    main()
