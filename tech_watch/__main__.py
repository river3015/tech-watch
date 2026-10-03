import argparse
import functools
import http.server
import json
from pathlib import Path
from .collector import collect
from .site import build


def main():
    parser = argparse.ArgumentParser(description='Collect feeds and build a personal tech journal')
    parser.add_argument('command', choices=['collect', 'build', 'run', 'serve'])
    parser.add_argument('--config', default='config/sources.json')
    parser.add_argument('--data', default='data')
    parser.add_argument('--output', default='public')
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()
    report = None
    if args.command in ('collect', 'run'):
        report = collect(args.config, args.data)
        for source in report['sources']:
            print(f'{source["name"]}: {source["status"]}, new={source["new"]}' + (f' ({source["error"]})' if source['status'] == 'error' else ''))
        print(f'Success: {report["successes"]}, failure: {report["failures"]}')
    if args.command in ('build', 'run', 'serve'):
        print(f'Built {build(args.data, args.output)} daily pages in {args.output}')
    if args.command == 'serve':
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(Path(args.output).resolve()))
        with http.server.ThreadingHTTPServer(('127.0.0.1', args.port), handler) as server:
            print(f'http://localhost:{args.port} (loopback only)', flush=True)
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                pass
    if report and report['successes'] == 0:
        raise SystemExit(1)

if __name__ == '__main__':
    main()
