#!/usr/bin/env python3

import socket
import logging

HOST = '127.0.0.1'
PORT = 65000

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
	s.bind((HOST, PORT))
	s.listen()
	connection, address = s.accept()
	with connection:
		logging.basicConfig(level=logging.INFO)
		connected_message = 'Connected by ' + address[0] + ':' + str(address[1])
		logging.info(connected_message)
		while True:
			data = connection.recv(1024)
			if not data:
				break
			connection.sendall(data)

