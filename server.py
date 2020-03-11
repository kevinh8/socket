# server.py

import socket

s = socket.socket()
host = "127.0.0.1"
port = 8081
s.bind((host, port))

s.listen(5)

i = 0
for i in range(5):
	i = i + 1
	c, address = s.accept()
	print("Receieved connection from", address)
	c.send("Thanks for connecting".encode("UTF-8"))
	c.close()
s.close()
