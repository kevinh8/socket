#/usr/bin/env python3

"""Implementation of a multi-connection server using sockets."""

__author__ = "Kevin Huang"
__email__ = "kevin.sing.huang@gmail.com"

import socket
import types
import selectors

HOST = '127.0.0.1'
PORT = 65000

def accept_wrapper(sock):
	connection, address = sock.accept()
	print("Accepted connection from " + address[0] + ':' + str(address[1]))
	connection.setblocking(False)
	data = types.SimpleNamespace(address=address, inb=b'', outb=b'')
	events = selectors.EVENT_READ | selectors.EVENT_WRITE
	sel.register(connection, events, data=data) 

def service_connection(key, mask):
	sock = key.fileobj
	data = key.data 
	if mask & selectors.EVENT_READ:
		recv_data = sock.recv(1024)
		if recv_data:
			data.outb += recv_data
		else:
			print("Closing connection to client " + str(data.address[0]) + ":" +  str(data.address[1]))
			sel.unregister(sock)
			sock.close()
	if mask & selectors.EVENT_WRITE:
		if data.outb:
			print("Sending; " + repr(data.outb) + ", to client on " + data.address[0] + ":" + str(data.address[1]))
			sent = sock.send(data.outb)
			data.outb = data.outb[sent:]

sel = selectors.DefaultSelector()

listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listen_sock.bind((HOST, PORT))
listen_sock.listen()
print("Started server on " + HOST + ":" + str(PORT))
listen_sock.setblocking(False)
sel.register(listen_sock, selectors.EVENT_READ, data=None)

while True:
	events = sel.select(timeout=None)
	for key, mask in events: 
		if key.data is None:
			accept_wrapper(key.fileobj) 
		else:
			service_connection(key, mask)
