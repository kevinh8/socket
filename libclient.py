#!/usr/bin/env python3

"""Implementation of an application client library using sockets."""

__author__ = "Kevin Huang"
__email__ = "kevin.sing.huang@gmail.com"


import selectors
import sys
import json
import struct

class Message:
    def __init__(self, selector, sock, address, request):
        self.selector = selector
        self.sock = sock
        self.address = address
        self.request = request
        self._request_queued = False
        self._send_buffer = b''
        self._json_header_len = None
        self.json_header = None
        self.response = None
        self._recv_buffer = b''

    def process_events(self, mask):
        if mask & selectors.EVENT_READ:
            self.read()
        if mask & selectors.EVENT_WRITE:
            self.write()

    def read(self):
        self._read()

        if self._json_header_len is None:
            self.process_protoheader()
        
        if self._json_header_len is not None:
            if self.json_header is None:
                self.process_jsonheader()
        
        if self.json_header is not None:
            if self.response is None:
                self.process_response()

    def write(self):
        if not self._request_queued:
            self.queue_request()
        
        self._write()

        if self._request_queued:
            if not self._send_buffer:
                self._set_selector_events_mask('r')

    def close(self):
        print('Closing connection to', self.address)
        try:
            self.selector.unregister(self.sock)
        except Exception as e:
            print('Error unregistering the socket')

        try:
            self.sock.close()
        except OSError as e:
            print('Error closing the socket')
        finally:
            self.sock = None

    def queue_request(self):
        content = self.request['content']
        content_type = self.request['type']
        content_encoding = self.request['encoding']
        if content_type == "text/json":
            req = {
                'content_bytes': self._json_encode(content, content_encoding),
                'content_type': content_type,
                'content_encoding': content_encoding
            }
        else:
            req = {
                'content_bytes': content,
                'content_type': content_type,
                'content_encoding': content_encoding
            }
        message = self._create_message(**req)
        self._send_buffer += message 
        self._request_queued = True

    def process_protoheader(self):
        hdrlen = 2
        if len(self._recv_buffer) >= hdrlen:
            self._json_header_len = struct.unpack(">H", self._recv_buffer[:hdrlen])[0]
            self._recv_buffer = self._recv_buffer[hdrlen:]

    def process_jsonheader(self):
        hdrlen = self._json_header_len
        if len(self._recv_buffer) >= hdrlen:
            self.json_header = self._json_decode(self._recv_buffer[:hdrlen], 'utf-8')
            self._recv_buffer = self._recv_buffer[hdrlen:]
            for reqhdr in ('byteorder', 'content-length', 'content-type', 'content-encoding'):
                if reqhdr not in self.json_header:
                    raise ValueError(f'Missing required header "{reqhdr}".')

    def process_response(self):
        content_length = self.json_header['content-length']
        if not len(self._recv_buffer) >= content_length:
            print("Something went wrong in determining the content-length")
            return
        data = self._recv_buffer[:content_length]
        self._recv_buffer = self._recv_buffer[content_length:]
        if self.json_header['content-type'] == 'text/json':
            encoding = self.json_header['content-encoding']
            self.request = self._json_decode(data, encoding)
            print("Received request", repr(self.request), 'from', self.address)
        else:
            self.request = data
            print("Received request", repr(self.request), 'from', self.address)
        self.close()

    def _read(self):
        try:
            data = self.sock.recv(4096)
        except BlockingIOError:
            pass
        else:
            if data:
                self._recv_buffer += data 
            else:
                raise RuntimeError('Peer closed.')

    def _write(self):
        if self._send_buffer:
            print("Sending", repr(self._send_buffer), "to", self.address)
            try:
                sent = self.sock.send(self._send_buffer)
            except BlockingIOError:
                pass
            else:
                print("Message successfully sent")
                self._send_buffer = self._send_buffer[sent:]

    def _set_selector_events_mask(self, mask):
        if mask == "w":
            event = selectors.EVENT_WRITE
        elif mask == "r":
            event = selectors.EVENT_READ
        elif mask == "rw":
            event = selectors.EVENT_READ | selectors.EVENT_WRITE
        else:
            raise ValueError(f"Invalid mask type {repr(mask)}")
        self.selector.modify(self.sock, event, data=self)

    def _json_encode(self, content, encoding):
        json_content = json.dumps(content)
        return json_content

    def _json_decode(self, content, encoding):
        json_decoded = content.decode(encoding)
        json_content = json.loads(json_decoded)
        return json_content

    def _create_message(self, *, content_bytes, content_type, content_encoding):
        jsonheader = {
            "byteorder": sys.byteorder,
            "content-type": content_type,
            "content-encoding": content_encoding,
            "content-length": len(content_bytes)
        }
        jsonheader_bytes = json.dumps(jsonheader)
        message_hdr = struct.pack(">H", len(jsonheader_bytes))
        message = message_hdr + bytes(jsonheader_bytes, content_encoding) + bytes(content_bytes, content_encoding)
        return message