#!/usr/bin/env python3
"""Local preview server for the site: python3 serve.py [port]

Same as `python3 -m http.server`, but with HTTP Range support, which
that module lacks. Without Range requests browsers cannot seek in
<audio>/<video> elements (the web player) — seeking silently snaps
back to the already-buffered position.

The production server must also support Range requests; verify with
  curl -sI -H 'Range: bytes=0-1' https://petmanson.com/<some>.mp3 | head -1
which should report "206 Partial Content" (nginx/apache do this out
of the box).
"""
import os
import re
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer


class RangeRequestHandler(SimpleHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def send_head(self):
        self.range = None
        match = re.match(r'bytes=(\d*)-(\d*)$',
                         self.headers.get('Range', '').strip())
        path = self.translate_path(self.path)
        if not match or not os.path.isfile(path):
            return super().send_head()

        try:
            f = open(path, 'rb')
        except OSError:
            self.send_error(404, 'File not found')
            return None
        stat = os.fstat(f.fileno())
        size = stat.st_size

        first, last = match.group(1), match.group(2)
        if first == '':
            # Suffix range: the last N bytes.
            if last == '' or int(last) == 0:
                start, end = size, 0  # forces 416 below
            else:
                start, end = max(0, size - int(last)), size - 1
        else:
            start = int(first)
            end = min(int(last), size - 1) if last != '' else size - 1
        if start >= size or start > end:
            f.close()
            self.send_response(416, 'Requested Range Not Satisfiable')
            self.send_header('Content-Range', 'bytes */%d' % size)
            self.send_header('Content-Length', '0')
            self.end_headers()
            return None

        self.range = (start, end)
        self.send_response(206, 'Partial Content')
        self.send_header('Content-Type', self.guess_type(path))
        self.send_header('Accept-Ranges', 'bytes')
        self.send_header('Content-Range', 'bytes %d-%d/%d' % (start, end, size))
        self.send_header('Content-Length', str(end - start + 1))
        self.send_header('Last-Modified', self.date_time_string(stat.st_mtime))
        self.end_headers()
        return f

    def copyfile(self, source, outputfile):
        if self.range is None:
            return super().copyfile(source, outputfile)
        start, end = self.range
        source.seek(start)
        remaining = end - start + 1
        while remaining > 0:
            chunk = source.read(min(64 * 1024, remaining))
            if not chunk:
                break
            outputfile.write(chunk)
            remaining -= len(chunk)


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    server = ThreadingHTTPServer(('', port), RangeRequestHandler)
    print('Serving on http://localhost:%d (with Range support)' % port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
