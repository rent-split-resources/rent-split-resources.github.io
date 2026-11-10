"""Build and serve a local preview: python preview.py [--port 8000]."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from build import PROJECT, build

def build_preview(port):
    directory = PROJECT / '.preview' / 'local-site'
    build(f'http://localhost:{port}', output=directory)
    return directory


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()
    directory = build_preview(args.port)
    handler = partial(SimpleHTTPRequestHandler, directory=str(directory))
    print(f'Preview: http://localhost:{args.port} (Ctrl+C to stop)', flush=True)
    with ThreadingHTTPServer(('127.0.0.1', args.port), handler) as server:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print('\nPreview stopped.')


if __name__ == '__main__':
    main()
