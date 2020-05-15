#!/usr/bin/env python3

"""Implementation of an application server using sockets."""

__author__ = "Kevin Huang"
__email__ = "kevin.sing.huang@gmail.com"

import sys
import socket
import selectors
import traceback

import libserver

try:
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
except IndexError:
    raise SystemExit(f"Usage: {sys.argv[0]} <server_ip> <server_port>")

def accept_wrapper(sock):
    conn, addr = sock.accept()
    print('Accepted connection for:', addr)
    conn.setblocking(False)
    message = libserver.Message(sel, conn, addr)
    sel.register(conn, selectors.EVENT_READ, data=message)

sel = selectors.DefaultSelector()

listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listen_sock.bind((HOST, PORT))
listen_sock.listen()
print('Listening on', (HOST, PORT))
sel.register(listen_sock, selectors.EVENT_READ, data=None)

while True:
    events = sel.select(timeout=None)
    for key, mask in events:
        if key.data is None:
            accept_wrapper(key.fileobj)
        else:
            message = key.data
            try:
                message.process_events(mask)
            except Exception:
                    print('ERROR: Exception for', f'{message.addr}:\n{traceback.format_exc()}')
                    message.close()
