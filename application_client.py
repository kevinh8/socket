#!/usr/bin/env python3

"""Implementation of an application client using sockets."""

__author__ = "Kevin Huang"
__email__ = "kevin.sing.huang@gmail.com"


import sys
import socket
import selectors

import libclient

try:
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    ACTION = sys.argv[3]
    VALUE = sys.argv[4]
except IndexError:
    raise SystemExit(f"Usage: {sys.argv[0]} <server_ip> <server_port> <action> <value>")

def start_connection(host, port, request):
    addr = (host, port)
    print("Starting conneciton to;", addr)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(addr)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    message = libclient.Message(sel, sock, addr, request)
    sel.register(sock, events, data=message)

# Creates a request by returning a dictionary 
def create_request(action, value):
    if action == "search":
        return dict(
            type="text/json",
            encoding="utf-8",
            content=dict(action=action, value=value)
        )
    else:
        return dict(
            type="binary/custom-client-binary-type",
            encoding="binary",
            content=bytes(action + value, "utf-8")
        )

sel = selectors.DefaultSelector()
request = create_request(ACTION, VALUE)
start_connection(HOST, PORT, request)

while True:
    events = sel.select(timeout=None)
    for key, mask in events:
        message = key.data
        try:
            message.process_events(mask)
        except Exception:
            print("Error in processing events")
            message.close()