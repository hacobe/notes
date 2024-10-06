# Socket programming

A **socket** is an interface that the operating system provides for sending and receiving data between 2 processes within a computer or across computers.

To initiate communication, a process starts by opening a socket. Opening a socket requires specifying an **address family** and a **communication protocol**. We'll only discuss the IPv4 address family, where an address consists of a version 4 IP address and a port number. We'll first discuss 2 communication protocols: 1) the **User Datagram Protocol (UDP)** and 2) the **Transmission Control Protocol (TCP)**.

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

We could also construct the UDP header ourselves using the `struct` library to pack bytes:

```python
def client():
	# SOCK_RAW directs the operating system to skip adding a transport layer header
	# (e.g., a UDP or TCP header) to the message. It will still add the network layer header.
	# IPPROTO_UDP tells the operating system that the socket will be used to send and receive UDP packets.
	s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
	s.bind((HOST, CLIENT_PORT))
	udp_length = 8 + len(MESSAGE)
	checksum = 0  # optional
	udp_header = struct.pack("!HHHH", CLIENT_PORT, SERVER_PORT, udp_length, checksum)
	s.sendto(udp_header + MESSAGE, (HOST, SERVER_PORT))
	print(f"{HOST}:{CLIENT_PORT} sent message {MESSAGE} to {HOST}:{SERVER_PORT}")
	s.close()
```

Constructing headers for lower layers with the `socket` library presents some difficulties when using Mac OS. We could use `scapy` to do it though. We could also set fields in lower layers via `socket.setsockopt`.

We turn our attention to TCP now. In TCP, the client process establishes a connection with a specific address. The server process listens at a specific address. It then accepts an incoming connection, which returns a socket for the connection and the address associated with the client's socket. The client then sends a message. The message is divided in packets and each packet is assigned a sequence number. Using the sequence numbers, the packets are reassembled in the correct order. The server process receives part of the message from the socket for the connection. Because the server only receives only part of the message, the server needs to keep calling receive until the OS signals that the client has closed the connection by returning an empty message or until the server determines that the client has sent a complete message based on some convention. TCP is a stream-oriented protocol as opposed to a message-oriented protocol like UDP.

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

We'll discuss one other protocol that operates at the Network layer rather than the Transport layer like UDP and TCP. The **Internet Control Message Protocol (ICMP)** is used by network devices to send error messages. The ICMP header appears after the IP header. The `traceroute` command uses ICMP to trace the path a packet traverses from your computer through the Internet to reach some destination. In particular, it sends a packet with an IP header that has a TTL (a better name is "hop count") set to the number of nodes that the packet can pass through before being discarded and generating an ICMP error message. It sets the TTL to 1 to find the first node. It sets the TTL to 2 to find the second node and so on. Here's an example that prints the IP address of the third node on the way to wikipedia.org:

```python
import socket
import struct

def compute_internet_checksum(message):
	# https://en.wikipedia.org/wiki/Internet_checksum
	total = 0
	for i in range(0, len(message), 2):
		total += (message[i] << 8) + message[i+1]
		total = (total & 0xffff) + (total >> 16)
	return ~total & 0xffff

def main():
	# SOCK_RAW directs the operating system to skip adding a transport layer header
	# (e.g., a UDP or TCP header) to the message. It will still add the network layer header.
	# IPPROTO_ICMP tells the operating system that the socket will be used to send and receive ICMP packets.
	s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
	# Set a field in the IPv4 header without having to write the entire header.
	s.setsockopt(socket.SOL_IP, socket.IP_TTL, 3)

	# Construct the ICMP header.
	# We need to use an ICMP socket to receive the ICMP error message, but we could use a
	# UDP socket to send the message with the TTL. Here we use an ICMP socket for both sending the
	# message with the TTL and receiving the ICMP error message.
	rtype = 8  # echo request
	rcode = 0
	checksum = 0
	# https://www.rfc-editor.org/rfc/rfc792 has the structure of the rest of the header.
	identifier = 0
	seq_num = 0
	outbound_message_with_zero_checksum = struct.pack("!BBHHH", rtype, rcode, checksum, identifier, seq_num)
	checksum = compute_internet_checksum(outbound_message_with_zero_checksum)
	outbound_message = struct.pack("!BBHHH", rtype, rcode, checksum, identifier, seq_num)
	wikipedia_org_ip_addr = "198.35.26.96"
	s.sendto(outbound_message, (wikipedia_org_ip_addr, 33434))

	# Receive and parse the ICMP error message.
	inbound_message, inbound_addr = s.recvfrom(4096)
	source_ip = ".".join([str(x) for x in inbound_message[12:16]])
	print(source_ip)

if __name__ == "__main__":
	main()
```

## Sources

* https://csprimer.com/watch/sockets/
* https://csprimer.com/watch/tcp-udp/
* https://csprimer.com/watch/shout-server/
* https://csprimer.com/watch/traceroute/
* https://beej.us/guide/bgnet/html/split/index.html
* https://web.archive.org/web/20240421145255/https://www.cs.dartmouth.edu/~campbell/cs60/socketprogramming.html
* https://en.wikipedia.org/wiki/Internet_Control_Message_Protocol