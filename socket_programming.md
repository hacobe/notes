# Socket programming

A **socket** is an interface that the operating system provides for sending and receiving data between 2 processes within a computer or across computers.

To initiate communication, a processs starts by opening a socket. Opening a socket requires specifying an **address family** and a **communication protocol**. We will only discuss the IPv4 address family, where an address consists of a version 4 IP address and a port number. We will discuss 2 communication protocols: 1) the **User Datagram Protocol (UDP)** and 2) the **Transmission Control Protocol (TCP)**.

In UDP, the client process sends a message to a specific address. The server process then receives the message and the address associated with the client's socket.

```
UDP client                                     UDP server

socket()                                       socket()
bind(client_ip, client_port)                   bind(server_ip, server_port)
                                               recvfrom()   
                                                   | # blocks until it receives a message
sendto(msg, (server_id, server_port)) -----------> |
                                                   -> msg, (client_ip, client_port) 
```

In TCP, the client process establishes a connection with a specific address and then sends a message. The server listens at a specific address. It then accepts an incoming connection, which returns a socket for the connection and the address associated with the client's socket. It then receives a message from the socket for the connection.

```
TCP client                                     TCP server

socket()                                       socket()
bind(host, client_port)                        bind(host, server_port)
                                               listen()   
                                               accept()
                                                   | # blocks until it receives a connection
connect((host, server_port)) --------------------> |
                                                   -> conn_socket, (host, client_port)
                                               conn_socket.recv()
send(msg) ---------------------------------------> |
                                                   | # blocks until it receives a message
                                                   -> msg
```

We show an example of UDP and TCP in Python:

```python
import multiprocessing
import socket

HOST = "127.0.0.1"
CLIENT_PORT = 8000
SERVER_PORT = 8888
MESSAGE = b"hello"
BUFFER_SIZE = 1024

def server(socket_type):
	"""Receive a message from the client socket."""
	s = socket.socket(
		# Specify the address family.
		# The address family determines the format of the address.
		# In this case, we use AF_INET, i.e., IPv4, so the format of the
		# address is a (host, port) tuple.
		family=socket.AF_INET,
		type=socket_type
	)
	# Bind, or associate, this socket with a specific address.
	s.bind((HOST, SERVER_PORT))

	if socket_type == socket.SOCK_DGRAM: 
		# Use the User Datagram Protocol (UDP).
		message, (host, port) = s.recvfrom(BUFFER_SIZE)
	else:
		# Use the Transmission Control Protocol (TCP).
		assert socket_type == socket.SOCK_STREAM
		# The number of connections allowed to wait in the queue
		# until accepted.
		backlog = 1
		s.listen(backlog)
		c, (host, port) = s.accept()
		message = c.recv(BUFFER_SIZE)

	print(f"{HOST}:{SERVER_PORT} received message {message} from {host}:{port} using socket type {socket_type}")
	assert host == HOST
	assert port == CLIENT_PORT
	assert message == MESSAGE

	s.close()

def client(socket_type):
	"""Send a message to the server socket."""
	s = socket.socket(family=socket.AF_INET, type=socket_type)
	s.bind((HOST, CLIENT_PORT))

	if socket_type == socket.SOCK_DGRAM:
		s.sendto(MESSAGE, (HOST, SERVER_PORT))
	else:
		s.connect((HOST, SERVER_PORT))
		s.send(MESSAGE)

	print(f"{HOST}:{CLIENT_PORT} sent message {MESSAGE} to {HOST}:{SERVER_PORT} using socket type {socket_type}")
	s.close()

def main(socket_type):
	p_server = multiprocessing.Process(target=server, args=(socket_type,))
	p_server.start()

	# If client sends its message before the server is ready
	# to receive the message, then the server will just sit
	# around waiting to receive a message that has already
	# been sent.

	p_client = multiprocessing.Process(target=client, args=(socket_type,))
	p_client.start()

	p_client.join()
	p_server.join()

if __name__ == "__main__":
	main(socket.SOCK_DGRAM)
	main(socket.SOCK_STREAM)
```

## Sources

* https://csprimer.com/watch/sockets/
* https://csprimer.com/watch/tcp-udp/
* https://csprimer.com/watch/shout-server/
* https://beej.us/guide/bgnet/html/split/index.html
* https://web.archive.org/web/20240421145255/https://www.cs.dartmouth.edu/~campbell/cs60/socketprogramming.html