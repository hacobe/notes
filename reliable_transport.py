"""Implement reliable transport.

The set up is that we have a client, proxy and server:

```
Client <------> Proxy <------> Server
port:6000       port:7000      port:8000          
```

The client sends a message to the proxy and the proxy forwards the message to server.
The server sends a messages to the proxy and the proxy forwards the message to the client.
The proxy may drop, duplicate or reorder messages.

The goal of the exercise is to write an interface that the client can use to send a
large message (larger than the maximum transmission unit) and the server can use to receive
that message and vice versa (i.e., bidirectional communication).

The interface will have to:
* segment the large message into packets and send those smaller packets
* ensure that the recipient can reconstruct the message by arranging packets in the correct order
* resend lost packets
* deduplicate packets sent multiple times

The interface will look like this:

client:

```python
conn = Connection(to_addr=("127.0.0.1", 7000))
conn.bind(("127.0.0.1", 6000))

# Blocks until the message has been acknowledged.
conn.send(b"aaaabbbbcccc\n\n\n\n")

response = b""
while True:
	# For simplicity, we'll receive 1 packet at a time.
	# Similar to the system recv method, we don't necessarily receive
	# the entire message. Different from that method, we receive
	# 1 packet instead of up to `bufsize` bytes.
	message = conn.recv()
	print(message)
	response += message
	if response.find(b"\n\n\n\n") != -1:
		break
```

server:

```python
conn = Connection(to_addr=("127.0.0.1", 7000))
conn.bind(("127.0.0.1", 8000))

request = b""
while True:
	message = conn.recv()
	print(message)
	request += message
	if message.find(b"\n\n\n\n") != -1:
		break

conn.send(b"xxxxyyyyzzzz\n\n\n\n")
```

The server starts receiving. The client starts sending. The server receives until
it gets a "\n\n\n\n" message, which indicates that the client is ready to receive.
Then, the server starts sending and the client starts receiving. Note that the application
layer determines when a process should send and when it should receive (in HTML, we have,
e.g., the content length in the header, which plays a similar role).

We start the client, server and proxy as follows:

```python
python reliable_transport.py client \
	--inbound_port 6000 \
	--outbound_host="127.0.0.1" \
	--outbound_port 7000
```

```python
python reliable_transport.py server \
	--inbound_port=8000 \
	--outbound_host="127.0.0.1" \
	--outbound_port=7000
```

```python
python lossy_proxy.py \
	--inbound_port=7000 \
	--upstream_host="127.0.0.1" \
	--upstream_port=8000 \
	--drop_rate=0.5 \
	--dup_rate=0.5 \
	--reorder_rate=0.5
```

Here's the communication flow:

```
Client                                                    Server
------                                                    ------
                                                          # iteration 0
                                                          recv()
                                                              recvfrom()
send("aaaa\n\n\n\n")
   # iteration 0                                      
   sendto("0aaaa")
                            --0aaaa-->
   # wait for ack
   recvfrom() 
                                                              -> 0aaaa
                                                              # send ack
                                                              sendto("0")
                                                  <--0--
                                                          # return to caller
                                                          -> 0aaaa
                                                          # iteration 1
                                                          recv()
                                                              recvfrom()
   -> 0
   # iteration 1
   sendto("1\n\n\n\n")
                            # dropped packet
                            # (note that from the
                            #  perspective of the
                            #  client this has
                            #  the same effect as if
                            #  the ack was dropped)
                            --1\n\n\n\n-->X
   recvfrom()
   -> timeout
   # iteration 2
   # retry
   sendto("1\n\n\n\n")
                            --1\n\n\n\n-->
   # wait for ack
   recvfrom()
                                                              -> 1\n\n\n\n
                                                              # send ack
                                                              sendto("1")
                                                   <--1--
                                                          -> 1\n\n\n\n
                                                          # start sending
                                                          send("xxxx\n\n\n\n")
   -> 1                                                   ...
# start receiving
recv()
...                                                       
  
```

Notes:
* Rely on a client sends a message and either receives an acknowledgement from the server
  or retries sending the message. The server receives a message from the client
  and sends an acknowledgement. If the client does not receive the acknowledgement,
  it can send the message again and the server will get another opportunity to acknowledge.
* The send function blocks until it has received an acknowledgment.
* The receive function does not have to return the whole message. It can just return what
  it has received so far that does not have packet gaps. The caller should keep calling receive
  to ensure that they get the whole message.

Sources:
* https://csprimer.com/watch/reliable-transport/
"""
import socket
import struct
import sys

_PACKET_NBYTES = 4

class Connection:

	def __init__(self, to_addr, timeout=1):
		self._s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self._s.settimeout(timeout)
		self._to_addr = to_addr

		# We need these, because recv doesn't block until the end of the message.
		self._seq_num_to_packet_body = {}
		self._ack_seq_num = 0

	def bind(self, addr):
		self._s.bind(addr)

	def send(self, message):
		# Segment the message into packets.
		packets = []
		seq_num = 0
		for start in range(0, len(message), _PACKET_NBYTES):
			end = start + _PACKET_NBYTES
			packet_body = message[start:end]
			packet_header = struct.pack("!H", seq_num)
			packet = packet_header + packet_body
			packets.append(packet)
			seq_num += 1

		# Send the packets and keep retrying until all packets
		# have been acknowledged.
		packet_start = 0
		while packet_start < len(packets):
			for i in range(packet_start, len(packets)):
				self._s.sendto(packets[i], self._to_addr)
			
			try:
				maybe_ack_message, from_addr = self._s.recvfrom(4096)
			except socket.timeout:
				continue

			# Skip any duplicate data messages that might be left over
			# when a caller goes from receiving to sending.
			# (data message has a body)
			if maybe_ack_message[2:]:
				continue

			ack_seq_num = struct.unpack("!H", maybe_ack_message)[0]
			packet_start = ack_seq_num + 1

	def recv(self):
		while True:
			if self._ack_seq_num in self._seq_num_to_packet_body:
				packet_body = self._seq_num_to_packet_body[self._ack_seq_num]
				ack_message = struct.pack("!H", self._ack_seq_num)
				self._s.sendto(ack_message, self._to_addr)
				self._ack_seq_num += 1
				return packet_body

			try:
				maybe_data_message, from_addr = self._s.recvfrom(4096)
			except socket.timeout:
				continue
			
			seq_num = struct.unpack("!H", maybe_data_message[:2])[0]
			packet_body = maybe_data_message[2:]

			# Skip any duplicate acknowledgment messages that might be left over
			# when a caller goes from sending to receiving.
			# (acknowledgment has no body)
			if not packet_body:
				continue

			self._seq_num_to_packet_body[seq_num] = packet_body

def client():
	conn = Connection(to_addr=("127.0.0.1", 7000))
	conn.bind(("127.0.0.1", 6000))

	# Blocks until the message has been acknowledged.
	conn.send(b"aaaabbbbcccc\n\n\n\n")

	response = b""
	while True:
		message = conn.recv()
		print(message)
		response += message
		if response.find(b"\n\n\n\n") != -1:
			break

def server():
	conn = Connection(to_addr=("127.0.0.1", 7000))
	conn.bind(("127.0.0.1", 8000))

	request = b""
	while True:
		message = conn.recv()
		print(message)
		request += message
		if message.find(b"\n\n\n\n") != -1:
			break

	conn.send(b"xxxxyyyyzzzz\n\n\n\n")

if __name__ == "__main__":
	if sys.argv[1] == "client":
		client()
	else:
		assert sys.argv[1] == "server"
		server()