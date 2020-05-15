#!/usr/bin/env python3

"""Implementation of an application server library using sockets."""

__author__ = "Kevin Huang"
__email__ = "kevin.sing.huang@gmail.com"

import struct
import selectors
import json
import sys

request_search = {
    "manifest": "clear or obvious to the eye or mind.",
    "humble": "having or showing a modest or low estimate of one's importance.",
    "kin": "one's family and relations.",
    "hygge": "a quality of cosiness and comfortable conviviality that engenders a feeling of contentment or well-being.",
    "lykke": "the danish word for happiness",
}

class Message:
    def __init__(self, selector, sock, addr):
        self.selector = selector
        self.sock = sock
        self.addr = addr
        self._recv_buffer = b""
        self._jsonheader_len = None
        self.jsonheader = None
        self.request = None
        self._send_buffer = b""
        self.response_created = False
    
    def process_events(self, mask):
        if mask & selectors.EVENT_READ:
            self.read()
        if mask & selectors.EVENT_WRITE:
            self.write()
    
    def close(self):
        print('Closing connection to', self.addr)
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

    def read(self):
        self._read() 

        if self._jsonheader_len is None:
            self.process_protoheader()
        
        if self._jsonheader_len is not None:
            if self.jsonheader is None:
                self.process_jsonheader()
        
        if self.jsonheader:
            if self.request is None:
                self.process_request()

    def write(self):
        if self.request:
            if not self.response_created:
                self.create_response()
        
        self._write()

    def process_protoheader(self):
        header_len = 2
        if len(self._recv_buffer) >= header_len:
            self._jsonheader_len = struct.unpack('>H', self._recv_buffer[:header_len])[0] 
            self._recv_buffer = self._recv_buffer[header_len:]
    
    def process_jsonheader(self):
        header_len = self._jsonheader_len
        if len(self._recv_buffer) >= header_len:
            self.jsonheader = self._json_decode(self._recv_buffer[:header_len], 'utf-8')
            self._recv_buffer = self._recv_buffer[header_len:] 

            for reqheader in ('byteorder', 'content-length', 'content-type', 'content-encoding'):
                if reqheader not in self.jsonheader:
                    raise ValueError(f'Missing required header "{reqheader}".')

    def process_request(self):
        content_len = self.jsonheader['content-length']
        if not len(self._recv_buffer) >= content_len:
            print("Something went wrong because the receiving buffer does not equal to the content length")
            return
        data = self._recv_buffer[:content_len] 
        self._recv_buffer = self._recv_buffer[content_len:] 
        if self.jsonheader['content-type'] == 'text/json': 
                encoding = self.jsonheader['content-encoding']
                self.request = self._json_decode(data, encoding) 
                print('Received request', repr(self.request), 'from', self.addr)
        else:
            self.request = data
            print('Received request', repr(self.request), 'from', self.addr)
        self._set_selector_events_mask('w') 

    def create_response(self):
        if self.jsonheader['content-type'] == 'text/json':
            response = self._create_json_response()
        else: 
            response = self._create_binary_response()
        message = self._create_message(**response) 
        self.response_created = True 
        self._send_buffer += message 

    def _set_selector_events_mask(self, masktype):
        if masktype == "w":
            events = selectors.EVENT_WRITE
        elif masktype == "r":
            events = selectors.EVENT_READ
        elif masktype == "rw":
            events = selectors.EVENT_READ | selectors.EVENT_WRITE
        else:
            raise ValueError(f"Invalid mask type {repr(masktype)}")
        self.selector.modify(self.sock, events, data=self)
    
    def _create_json_response(self):
        action = self.request.get("action")
        if action == "search":
            query = self.request.get("value")
            answer = request_search.get(query) or f'No match for "{query}"."'
            content = {"result": answer}
        else:
            content = {"result": f'Error: invalid action "{action}".'}
        response = {
            "content_bytes": json.dumps(content),
            "content_type": "text/json",
            "content_encoding": "utf-8"
        }
        return response
    
    def _create_binary_response(self):
        response = {
            "content_bytes": b"First 10 bytes of request: " + self.request[:10],
            "content_type": "binary/custom-server-binary-type",
            "content_encoding": "binary",
        }
        return response

    def _create_message(self, *, content_bytes, content_type, content_encoding):
        jsonheader = {
            "byteorder": sys.byteorder,
            "content-type": content_type,
            "content-encoding": content_encoding,
            "content-length": len(content_bytes),
        }
        jsonheader_bytes = json.dumps(jsonheader)
        message_hdr = struct.pack(">H", len(jsonheader_bytes))
        message = message_hdr + bytes(jsonheader_bytes, content_encoding) + bytes(content_bytes, content_encoding)
        return message

    def _json_decode(self, recvbuffer, encodingtype):
        recvbuffer_json = recvbuffer.decode(encodingtype)
        decoded = json.loads(recvbuffer_json)
        return decoded

    def _write(self):
        if self._send_buffer:
            print('Sending', repr(self._send_buffer), 'to', self.addr)
            try:
                sent = self.sock.send(self._send_buffer)
            except BlockingIOError:
                pass
            else:
                self._send_buffer = self._send_buffer[sent:]
                if sent and not self._send_buffer:
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