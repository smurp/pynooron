

"""Augment medusa.http_server.http_channel."""

import re, string, sys
import traceback
import asyncore

if __name__ == "__main__":
    class http_request:
        pass
else:
    from medusa.http_server import http_channel
    from medusa.http_server import crack_request,\
         join_headers,\
         unquote,\
         http_request
    from NooronUser import NooronUser, NullUser


def found_terminator (self):
    if self.current_request:
        self.current_request.found_terminator()
    else:
        header = self.in_buffer
        self.in_buffer = ''
        lines = string.split (header, '\r\n')

        # --------------------------------------------------
        # crack the request header
        # --------------------------------------------------

        while lines and not lines[0]:
            # as per the suggestion of http-1.1 section 4.1, (and
            # Eric Parker <eparker@zyvex.com>), ignore a leading
            # blank lines (buggy browsers tack it onto the end of
            # POST requests)
            lines = lines[1:]

        if not lines:
            self.close_when_done()
            return

        request = lines[0]

        # unquote path if necessary (thanks to Skip Montaro for pointing
        # out that we must unquote in piecemeal fashion).
        if '%' in request:
            request = unquote (request)

        command, uri, version = crack_request (request)
        header = join_headers (lines[1:])

        r = http_request (self, request, command, uri, version, header)
        self.request_counter.increment()
        self.server.total_requests.increment()

        if command is None:
            self.log_info ('Bad HTTP request: %s' % repr(request), 'error')
            r.error (400)
            return

        # --------------------------------------------------
        # handler selection and dispatch
        # --------------------------------------------------
        for h in self.server.handlers:
            if h.match (r):
                try:
                    self.current_request = r
                    # This isn't used anywhere.
                    # r.handler = h # CYCLE
                    h.handle_request (r)
                except:
                    self.server.exceptions.increment()
                    (file, fun, line), t, v, tbinfo = asyncore.compact_traceback()
                    self.log_info(
                                    'Server Error: %s, %s: file: %s line: %s' % (t,v,file,line),
                                    'error')
                    try:
                        r.error (500)
                    except:
                        pass
                return

        # no handlers, so complain
        r.error (404)
http_channel.found_terminator = found_terminator

