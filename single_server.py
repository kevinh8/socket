#!/usr/bin/env python3

"""Implementation of a single connection server using sockets."""

__author__ = "Kevin Huang"
__email__ = "kevin.sing.huang@gmail.com"

import socket

HOST = '127.0.0.1'
PORT = 65000

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
	s.bind((HOST, PORT))
	s.listen()
	connection, address = s.accept()
	with connection:
		print("Client connected from " + address[0] + ":" + str(address[1]))
		while True:
			data = connection.recv(1024)
			if not data:
				break
			else:
				print("Received " + str(data) + " from client.")
			connection.sendall(data)