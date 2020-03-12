# server.py

import socket
import sys
# TODO: Implement listening and sending thread
import threading
# TODO: Implement arg parser
import argparse

host = sys.argv[1] #Exception handling
port = int(sys.argv[2]) #Exception handling

s = socket.socket()
# TODO: Exception handling for bindx
s.bind((host, port))
s.listen(3)

i = 0
# TODO: Function for sending thread
for i in range(5):
	i = i + 1
	c, address = s.accept()
	print("Receieved connection from", address)
	c.send("Thanks for connecting".encode("UTF-8"))
	
	c.close()

def sending():
	host = "127.0.0.1"
	port = 8087
	s = socket.socket()
	s.bind((host, port))
	s.listen(3)
	while True:
		c, address = s.accept()
		print("Recieved connection from ", address)
		c.send("Sending ... thanks for connecting".encode("UTF-8"))

# TODO: Function for listening thread
def listening(s):
	while True:
		print(s.recv(1024))

x = threading.Thread(target=sending, args=())
x.start()
sock = socket.socket()
sock.bind((host, 8090))
sock.listen(3)
y = threading.Thread(target=listening, args=(sock,))
y.start()
s.close()
