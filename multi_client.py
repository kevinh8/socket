#!/usr/bin/env python3

import logging
import socket
import types
import selectors
import pprint

messages = [b'Message 1 from client', b'Message 2 from client']

HOST = '127.0.0.1'
PORT = 65000
NUM_CONN = 1

def start_connections(host, port, num_connections):
    server_address = (host, port)
    for i in range(0, num_connections):
        connection_id = i + 1
        print('Starting connection ', connection_id, ' to ', server_address)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("SOCKET BEFORE = ")
        pp.pprint(sock)
        sock.setblocking(False)
        sock.connect_ex(server_address)
        print("SOCKET AFTER = ")
        pp.pprint(sock)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        print("EVENTS Bit-mask = ")
        print(events)
        print(type(events))
        print("SEL BEFORE = ")
        pp.pprint(sel.__dict__)
        data = types.SimpleNamespace(connection_id=connection_id,
											message_total=sum(len(m) for m in messages),
											recv_total=0,
											messages=list(messages),
											outb=b'')
        sel.register(sock, events, data=data)
        print("SEL AFTER = ")
        pp.pprint(sel.__dict__)

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        print("INSIDE EVENT READ")
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            print('received', repr(recv_data), 'from connection', data.connection_id)
            data.recv_total += len(recv_data)
        print("RECV_DATA ADDED = ")
        pp.pprint(key)
        if not recv_data or data.recv_total == data.message_total:
            print('closing connection', data.connection_id)
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        print("INSIDE EVENT WRITE")
        if not data.outb and data.messages:
            data.outb = data.messages.pop(0)
        print("After DATA inputted = ")
        pp.pprint(key)
        if data.outb:
            print('sending', repr(data.outb), 'to connection', data.connection_id)
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]
        print("AFTER 2nd IF = ")
        pp.pprint(key)

pp = pprint.PrettyPrinter(indent=4)

sel = selectors.DefaultSelector()
print("SEL = ")
pp.pprint(sel.__dict__)

start_connections(HOST, PORT, NUM_CONN)

while True:
    events = sel.select(timeout=None)
    print("EVENTS = ")
    pp.pprint(events)
    for key, mask in events:
        service_connection(key, mask)
