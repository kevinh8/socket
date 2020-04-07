#!/usr/bin/env python3

"""Implementation of a single connection client to server using sockets."""

__author__ = "Kevin Huang"
__email__ = "kevin.sing.huang@gmail.com"

import socket

HOST = '127.0.0.1'
PORT = 65000

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
	print("Connecting to server " + HOST + ":" + str(PORT))
	s.connect((HOST, PORT))
	s.sendall(b'Hello world!')
	data = s.recv(1024)

print("Receieved " + str(data) + " from server.")