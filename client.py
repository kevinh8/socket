# client.py

import socket
import sys

host = sys.argv[1]
port = int(sys.argv[2])
s = socket.socket()

# TODO: Handle connect exception
s.connect((host, port))
print("Successfully connected to server.")
print(s.recv(1024))
s.close()
print("Disconnected from the server.")
