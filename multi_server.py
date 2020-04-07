#/usr/bin/env python3

import pprint
import selectors
import socket
import logging
import types

HOST = '127.0.0.1'
PORT = 65000

def accept_wrapper(sock):
	connection, address = sock.accept()
	accept_message = 'Accepted connection from ' + address[0] + ':' + str(address[1])
	logging.info(accept_message)
	connection.setblocking(False)
	print("CONNECTION = ")
	pp.pprint(connection)
	# Creates a data object with values; address, inb and outb
	data = types.SimpleNamespace(address=address, inb=b'', outb=b'')
	print("CREATED DATA_TYPE = ")
	pp.pprint(data)
	# Bitwise OR operator 1 OR 2
	events = selectors.EVENT_READ | selectors.EVENT_WRITE
	# Register connection for reading or writing 
	sel.register(connection, events, data=data) 

def service_connection(key, mask):
	sock = key.fileobj # Get the file object (which is the socket)
	data = key.data # Get the data
	# If the socket is ready for reading mask & EVENT_READ == TRUE
	print("MASK1")
	print(mask)
	if mask & selectors.EVENT_READ:
		recv_data = sock.recv(1024)
		print("RECV_DATA = ")
		pp.pprint(recv_data)
		if recv_data:
			data.outb += recv_data # All data is appended to data.outb (created object)
		else: # Else, not sending data so we should close connection
			closing_message = "Closing connection to " + str(data.address[0]) + str(data.address[1])
			logging.info(closing_message)
			sel.unregister(sock) # Unregister from so select() is no longer monitoring
			sock.close()
		print("POST READ = ")
		pp.pprint(key)
		print("MASK2")
		print(mask)
	# If socket is ready for writing mask & EVENT_WRITE == TRUE
	if mask & selectors.EVENT_WRITE:
		if data.outb:
			print("Echoing ", repr(data.outb), " to ", data.address)
			sent = sock.send(data.outb) # sent = int of bytes send
			data.outb = data.outb[sent:] # clears the data / resets to []
		print("POST WRITE = ")
		pp.pprint(key)
		print("MASK2")
		print(mask)
	print("MASK3")
	print(mask)
pp = pprint.PrettyPrinter(indent=4)

# Creates default selector which is most efficient implementation
sel = selectors.DefaultSelector()
pp.pprint(sel.__dict__)

listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listen_sock.bind((HOST, PORT))
listen_sock.listen()
logging.basicConfig(level=logging.INFO)
listen_message = 'Listening on ' + HOST + ":" + str(PORT)
logging.info(listen_message)

# Sets socket to non-blocking mode allowing calls to not have to wait
listen_sock.setblocking(False)

# Monitoring the listening socket for IO events. selectors.EVENT_READ=int 1
# Registering the selector for reading events
sel.register(listen_sock, selectors.EVENT_READ, data=None)
pp.pprint(sel.__dict__)

while True:
	# Events will block UNTIL fileobj is ready to which will generate a (key, mask) tuple
	events = sel.select(timeout=None)
	print("EVENTS = ")
	pp.pprint(events)
	for key, mask in events: # Loop through tupple
		# If the SelectorKey has empty data, then it means a connection is to be accepted
		if key.data is None:
			print("EVENTS KEY.DATA == NONE = ")
			pp.pprint(events[0][0])
			pp.pprint(events[0][1])
			accept_wrapper(key.fileobj) # Parse in the fileobj of the event (socket)
		# Else, data has some value and we service the connection
		else:
			service_connection(key, mask)
