# Socket programming

A **socket** is an interface that the operating system provides for sending and receiving data between 2 processes within a computer or across computers.

To initiate communication, a processs starts by opening a socket. Opening a socket requires specifying an **address family** and a **communication protocol**. We will only discuss the IPv4 address family, where an address consists of a version 4 IP address and a port number. We will discuss 2 communication protocols: 1) the **User Datagram Protocol (UDP)** and 2) the **Transmission Control Protocol (TCP)**.

In UDP, the client process sends a message to a specific address. The server process then receives the message and the address associated with the client's socket. The server may truncate the message if the message size exceeds the buffer size set by the server.

```
UDP client                                     UDP server

socket()                                       socket()
bind(client_ip, client_port)                   bind(server_ip, server_port)
                                               recvfrom()   
                                                   | # blocks until it receives a message
sendto(msg, (server_id, server_port)) -----------> |
                                                   -> msg, (client_ip, client_port)
close()                                        close()
```

Here is an example of UDP in Python:

```python
import multiprocessing
import socket

HOST = "127.0.0.1"
CLIENT_PORT = 8000
SERVER_PORT = 8888
MESSAGE = b"hello"
BUFFER_SIZE = 1024

def server():
	"""Receive a message from the client socket."""
	s = socket.socket(
		# Specify the address family.
		# The address family determines the format of the address.
		# In this case, we use AF_INET, i.e., IPv4, so the format of the
		# address is a (host, port) tuple.
		family=socket.AF_INET,
		# Use the User Datagram Protocol (UDP).
		type=socket.SOCK_DGRAM
	)
	# Bind, or associate, this socket with a specific address.
	s.bind((HOST, SERVER_PORT))
	message, (host, port) = s.recvfrom(BUFFER_SIZE)
	print(f"{HOST}:{SERVER_PORT} received message {message} from {host}:{port}")
	s.close()

def client():
	"""Send a message to the server socket."""
	s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
	s.bind((HOST, CLIENT_PORT))
	s.sendto(MESSAGE, (HOST, SERVER_PORT))
	print(f"{HOST}:{CLIENT_PORT} sent message {MESSAGE} to {HOST}:{SERVER_PORT}")
	s.close()

def main():
	p_server = multiprocessing.Process(target=server)
	p_server.start()

	# If client sends its message before the server is ready
	# to receive the message, then the server will just sit
	# around waiting to receive a message that has already
	# been sent.

	p_client = multiprocessing.Process(target=client)
	p_client.start()

	p_client.join()
	p_server.join()

if __name__ == "__main__":
	main()
```

In TCP, the client process establishes a connection with a specific address. The server process listens at a specific address. It then accepts an incoming connection, which returns a socket for the connection and the address associated with the client's socket. The client then sends a message. The message is divided in packets and each packet is assigned a sequence number. Using the sequence numbers, the packets are reassembled in the correct order. The server process receives part of the message from the socket for the connection. Because the server only receives only part of the message, the server needs to keep calling receive until the OS signals that the client has closed the connection by returning an empty message or until the server determines that the client has sent a complete message based on some convention. TCP is a stream-oriented protocol as opposed to a message-oriented protocol like UDP.

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
                                                   | # blocks until it receives the first part of
                                                   | # the client's message (say packets 1 and 2)
send(msg) -----packet 1 -------------------------> |
          -----packet 3 -------------------------> |
          -----packet 2 -------------------------> |
                                                   -> msg[:k]
                                                   |
                                               conn_socket.recv()
                                                   | # blocks until it receives the second part
                                                   | # of the client's message (say packets 3, 4 and 5)
          -----packet 5 -------------------------> |
          -----packet 4 -------------------------> |
                                                   -> msg[k:]
close()                                            |
                                               conn_socket.recv()
                                                   | # The OS signals that the client has
                                                   | # closed the connection by returning
                                                   | # an empty message.
                                                   -> b''
                                                   |
                                               close()
```

Here is an example of TCP in Python (the code before the server function and after the client function are the same as the code above):

```python
def server():
	"""Receive a message from the client socket."""
	s = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
	# Bind, or associate, this socket with a specific address.
	s.bind((HOST, SERVER_PORT))
	# The number of connections allowed to wait in the queue
	# until accepted.
	backlog = 1
	s.listen(backlog)
	c, (host, port) = s.accept()
	while True:
		message = c.recv(BUFFER_SIZE)
		print(f"{HOST}:{SERVER_PORT} received message {message} from {host}:{port}")
		# The OS signals that the client has closed the connection
		# by returning an empty message.
		if not message:
			break
	s.close()

def client():
	"""Send a message to the server socket."""
	s = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
	s.bind((HOST, CLIENT_PORT))
	s.connect((HOST, SERVER_PORT))
	s.send(MESSAGE)
	print(f"{HOST}:{CLIENT_PORT} sent message {MESSAGE} to {HOST}:{SERVER_PORT}")
	s.close()
```

## Sources

* https://csprimer.com/watch/sockets/
* https://csprimer.com/watch/tcp-udp/
* https://csprimer.com/watch/shout-server/
* https://beej.us/guide/bgnet/html/split/index.html
* https://web.archive.org/web/20240421145255/https://www.cs.dartmouth.edu/~campbell/cs60/socketprogramming.html