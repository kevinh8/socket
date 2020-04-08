#!/usr/bin/env python3

"""Implementation of a multi-connection client to server using sockets."""

__author__ = "Kevin Huang"
__email__ = "kevin.sing.huang@gmail.com"

import socket
import types
import selectors

HOST = '127.0.0.1'
PORT = 65000
NUM_CONN = 1

messages = [b'Message 1 from client', b'Message 2 from client']

def start_connections(host, port, num_connections):
    server_address = (host, port)
    for i in range(0, num_connections):
        connection_id = i + 1
        print("Starting connection " + str(connection_id) + " to server " + HOST + ":" + str(PORT))
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(server_address)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        data = types.SimpleNamespace(connection_id=connection_id,
											message_total=sum(len(m) for m in messages),
											recv_total=0,
											messages=list(messages),
											outb=b'')
        sel.register(sock, events, data=data)

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data:
            print("Received; " + repr(recv_data) + ", from server on connection " + str(data.connection_id))
            data.recv_total += len(recv_data)
        if not recv_data or data.recv_total == data.message_total:
            print("Closing connection " + str(data.connection_id))
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if not data.outb and data.messages:
            data.outb = data.messages.pop(0)
        if data.outb:
            print("Sending; " + repr(data.outb) + ", to server on connection " + str(data.connection_id))
            sent = sock.send(data.outb)
            data.outb = data.outb[sent:]

sel = selectors.DefaultSelector()

start_connections(HOST, PORT, NUM_CONN)

while True:
    events = sel.select(timeout=None)
    for key, mask in events:
        service_connection(key, mask)