# HTTP proxy

## What is a reverse proxy?

In [HTTP semantics](https://www.rfc-editor.org/rfc/rfc9110.html), a **user agent** "refers to any of the various client programs that initiate a request" (typically a browser) and an **origin server** "refers to a program that can originate authoritative responses for a given target resource" (typically a web server). An **intermediary** is a program between the user agent and the origin server. One of the common forms of intermediaries is a **gateway**, or **reverse proxy**, which "acts as an origin server for the outbound connection but translates received requests and forwards them inbound to another server or servers." A reverse proxy like [nginx](https://nginx.org/en/) might take care of caching, security, compression, etc. so that the origin server can focus on application logic.

## Basics

### Implementation

We implement a reverse proxy that receives a request from the client, forwards it to an upstream HTTP server, receives the response from the upstream HTTP server, and returns the response to the client.

We start by creating a simple web page and starting our upstream server to serve the web page on port 9000:

```bash
> mkdir upstream
> cd upstream
> echo '<html><body>Hello!</body></html>' > index.html
> python -m http.server 9000
Serving HTTP on :: port 9000 (http://[::]:9000/) ...
```

We then implement our initial proxy server in `http_proxy.py`:

```python
import socket

def main():
	proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	proxy_socket.bind(("127.0.0.1", 8000))
	proxy_socket.listen(1)

	while True:  # keep accepting connections
		client_socket, (client_host, client_port) = proxy_socket.accept()

		# Try to catch errors to keep the proxy server up.
		try:
			# For simplicity, create a new connection to the upstream server.
			# Typically, we would want to try to keep the connection to the
			# upstream server alive.
			upstream_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			upstream_socket.connect(("127.0.0.1", 9000))

			client_request = b''
			while True:  # keep receiving from client
				client_message = client_socket.recv(4096)
				if not client_message:
					break
				upstream_socket.send(client_message)
				client_request += client_message
				# The proxy server's condition for ending a request.
				# Typically, the logic would be more complex and include
				# the request type and the Content-Length header.
				if client_request.endswith(b'\r\n\r\n'):
					break

			# We only expect to receive from upstream server if we've made
			# a request.
			if client_request:
				while True:  # keep receiving from upstream
					upstream_message = upstream_socket.recv(4096)
					if not upstream_message:
						break
					client_socket.send(upstream_message)

			upstream_socket.close()

		except ConnectionRefusedError:  # E.g., upstream server is down.
			# Without the Content-Length header, curl returns "curl: (56) Recv failure: Connection reset by peer".
			client_socket.send(b"HTTP/1.1 502 Bad Gateway\r\nContent-Length: 0\r\n\r\n")
		except OSError as msg:
			print(msg)
		finally:
			client_socket.close()

	proxy_socket.close()

if __name__ == "__main__":
	main()
```

### Testing

We then start our proxy server:

```bash
> python http_proxy.py
```

And send a request:

```bash
> curl localhost:8000
<html><body>Hello!</body></html>
```

The curl client sends the request b'GET / HTTP/1.1\r\nHost: localhost:8000\r\nUser-Agent: curl/8.1.1\r\nAccept: */*\r\n\r\n'. The HTTP/1.1 specification uses `\r\n` to separate lines in the header (see more [here](https://stackoverflow.com/questions/5757290/http-header-line-break-style)). It uses `\r\n\r\n` to denote the end of the headers section. A GET request typically does not have a body section.

We can curl multiple times.

We can also bring down the upstream server and then curl with the verbose flag:

```bash
> curl -v localhost:8000
*   Trying 127.0.0.1:8000...
* Connected to localhost (127.0.0.1) port 8000 (#0)
> GET / HTTP/1.1
> Host: localhost:8000
> User-Agent: curl/8.1.1
> Accept: */*
> 
< HTTP/1.1 502 Bad Gateway
< Content-Length: 0
< 
* Connection #0 to host localhost left intact
```

When we bring the upstream server back up and curl again:

```bash
> curl localhost:8000
<html><body>Hello!</body></html>
```

## Keepalive semantics

### Implementation

We modify our implementation to support keepalive semantics:

* HTTP/1.1: Keep the connection open unless "Connection: Close" is in the header
* HTTP/1.0: Close the connection unless "Connection: Keep-Alive" is in the header

We do not support HTTP/0.9, HTTP/2 or HTTP/3. HTTP/0.9 doesn't have headers and connection headers don't make sense in HTTP/2 and HTTP/3.

```python
import socket

def should_keep_alive(request):
	lines = request.split(b"\n")
	assert len(lines) >= 1
	method, uri, version = lines[0].rstrip().split(b' ')	
	connection = None
	for line in lines:
		if line.startswith(b"Connection: "):
			_, connection = line.split(b": ")
			connection = connection.strip()
	if version == b"HTTP/1.1" and (not connection):
		keep_alive = True
	elif version == b"HTTP/1.1" and connection == b"Close":
		keep_alive = False
	elif version == b"HTTP/1.0" and (not connection):
		keep_alive = False
	elif version == b"HTTP/1.0" and connection == b"Keep-Alive":
		keep_alive = True
	else:
		keep_alive = False
	return keep_alive

def main():
	proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	proxy_socket.bind(("127.0.0.1", 8000))
	proxy_socket.listen(1)

	while True:  # keep accepting connections
		client_socket, (client_host, client_port) = proxy_socket.accept()
		print("New connection")

		# Try to catch errors to keep the proxy server up.
		try:
			while True:  # keep connection alive
				# For simplicity, create a new connection to the upstream server.
				# Typically, we would want to try to keep the connection to the
				# upstream server alive.
				upstream_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				upstream_socket.connect(("127.0.0.1", 9000))

				client_request = b''
				while True:  # keep receiving from client
					client_message = client_socket.recv(4096)
					if not client_message:
						break
					upstream_socket.send(client_message)
					client_request += client_message
					# The proxy server's condition for ending a request.
					# Typically, the logic would be more complex and include
					# the request type and the Content-Length header.
					if client_request.endswith(b'\r\n\r\n'):
						break

				# We only expect to receive from upstream server if we've made
				# a request.
				if client_request:
					while True:  # keep receiving from upstream
						upstream_message = upstream_socket.recv(4096)
						if not upstream_message:
							break
						client_socket.send(upstream_message)

				upstream_socket.close()

				if (not client_request) or (not should_keep_alive(client_request)):
					break

		except ConnectionRefusedError:  # E.g., upstream server is down.
			# Without the Content-Length header, curl returns "curl: (56) Recv failure: Connection reset by peer".
			client_socket.send(b"HTTP/1.1 502 Bad Gateway\r\nContent-Length: 0\r\n\r\n")
		except OSError as msg:
			print(msg)
		finally:
			client_socket.close()

	proxy_socket.close()

if __name__ == "__main__":
	main()
```

### Testing

We test the keepalive semantics using netcat:

```bash
> nc localhost 8000
GET / HTTP/1.1^M
^M
```

`^M` is a special character created from pressing CTRL+V followed by CTRL+M that represents `\r` (similarly CTRL+V followed by CTRL+J, or `^J`, represents `\n`). After typing in the first line and pressing enter, the netcat client sends the message b'GET / HTTP/1.1\r\n'. After typing in the second line and pressing enter, the netcat client sends the message b'\r\n'. The netcat client then gets back the following response:

```bash
HTTP/1.0 200 OK
Server: SimpleHTTP/0.6 Python/3.11.3
Date: Mon, 17 Jun 2024 03:42:43 GMT
Content-type: text/html
Content-Length: 33
Last-Modified: Sun, 16 Jun 2024 15:18:48 GMT

<html><body>Hello!</body></html>
```

The proxy server keeps the client connection open.

We can also keep the connection open with HTTP/1.0. We continue in the netcat client:

```bash
GET / HTTP/1.0^M
Connection: Keep-Alive^M
^M
```

If we don't include the Connection header:

```bash
GET / HTTP/1.0^M
^M
```

Then the connection closes.

We can also close the connection with HTTP/1.1. Starting a new netcat client:

```bash
> nc localhost 8000
GET / HTTP/1.1^M
Connection: Close^M
^M
```

## Concurrency

### Implementation

We now modify our implementation to support accepting connections and reading from client sockets concurrently. For simplicity, we do not support concurrency for the upstream socket. We also do not support concurrent writing to sockets. With these constraints, the basic idea is to replace the nested while loops in the previous implementation with a single while loop and then to add a for loop through client sockets that are ready to read and the proxy socket if it's ready to accept a connection. We use the select system call to do this. Here is the implementation:

```python
import dataclasses
import socket
import select

@dataclasses.dataclass
class State:
	upstream_socket: socket.socket
	client_request: bytes

def should_keep_alive(request):
	lines = request.split(b"\n")
	assert len(lines) >= 1
	method, uri, version = lines[0].rstrip().split(b' ')	
	connection = None
	for line in lines:
		if line.startswith(b"Connection: "):
			_, connection = line.split(b": ")
			connection = connection.strip()
	if version == b"HTTP/1.1" and (not connection):
		keep_alive = True
	elif version == b"HTTP/1.1" and connection == b"Close":
		keep_alive = False
	elif version == b"HTTP/1.0" and (not connection):
		keep_alive = False
	elif version == b"HTTP/1.0" and connection == b"Keep-Alive":
		keep_alive = True
	else:
		keep_alive = False
	return keep_alive

def main():
	proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	proxy_socket.setblocking(False)
	proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	proxy_socket.bind(("127.0.0.1", 8000))
	proxy_socket.listen(1)

	rlist = [proxy_socket]
	client_socket_to_state = {}
	while True:  # event loop
		readable, _, _ = select.select(rlist, [], [])

		for s in readable:
			if s is proxy_socket:
				client_socket, (client_host, client_port) = proxy_socket.accept()
				client_socket.setblocking(False)
				rlist.append(client_socket)
				continue

			if s not in client_socket_to_state:
				upstream_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				upstream_socket.connect(("127.0.0.1", 9000))
				state = State(upstream_socket, b'')
				client_socket_to_state[s] = state
			state = client_socket_to_state[s]

			def execute_one_iteration_of_inner_loop():
				client_message = s.recv(4096)
				if not client_message:
					return True
				state.upstream_socket.send(client_message)
				state.client_request += client_message
				if state.client_request.endswith(b'\r\n\r\n'):
					return True
				return False
			done = execute_one_iteration_of_inner_loop()
			if not done:
				continue

			if state.client_request:
				while True:
					upstream_message = state.upstream_socket.recv(4096)
					if not upstream_message:
						break
					s.send(upstream_message)

			client_request = state.client_request  # copy
			state.upstream_socket.close()
			del client_socket_to_state[s]

			if (not client_request) or (not should_keep_alive(client_request)):
				s.close()
				rlist.remove(s)

	proxy_socket.close()

if __name__ == "__main__":
	main()
```

### Testing

To test the concurrency, open 3 tabs:

In tab 1:

```bash
> python http_proxy.py
```

In tab 2:

```bash
> nc localhost 8000
```

In tab 3:

```bash
> nc localhost 8000
GET / HTTP/1.0^M
^M
```

We should get back something like the following response:

```bash
HTTP/1.0 200 OK
Server: SimpleHTTP/0.6 Python/3.11.3
Date: Wed, 19 Jun 2024 18:37:28 GMT
Content-type: text/html
Content-Length: 33
Last-Modified: Sun, 16 Jun 2024 15:18:48 GMT

<html><body>Hello!</body></html>
```

## More features

### Implementation

We add the following features:
* Adding headers to the response
* Gzipping
* Caching

```python
import dataclasses
import datetime
import gzip
import re
import socket
import select
import time

CACHE = {}

@dataclasses.dataclass
class State:
	upstream_socket: socket.socket
	client_request: bytes

@dataclasses.dataclass
class HttpRequest:

	# request line
	method: bytes
	uri: bytes
	version: bytes

	headers: dict[bytes, bytes]
	body: bytes

@dataclasses.dataclass
class HttpResponse:

	# status line
	version: bytes
	status_code: bytes
	status_message: bytes

	headers: dict[bytes, bytes]
	body: bytes

def should_keep_alive(http_request):
	version = http_request.version
	connection = http_request.headers.get(b"Connection", None)
	if version == b"HTTP/1.1" and (not connection):
		keep_alive = True
	elif version == b"HTTP/1.1" and connection == b"Close":
		keep_alive = False
	elif version == b"HTTP/1.0" and (not connection):
		keep_alive = False
	elif version == b"HTTP/1.0" and connection == b"Keep-Alive":
		keep_alive = True
	else:
		keep_alive = False
	return keep_alive

def to_http_request(request):
	header_section, body = request.split(b"\r\n\r\n")
	header_section_lines = header_section.split(b"\r\n")
	request_line = header_section_lines[0]
	method, uri, version = request_line.rstrip().split(b' ', 2)
	headers = {}
	for i in range(1, len(header_section_lines)):
		key, value = header_section_lines[i].split(b": ")
		headers[key] = value
	return HttpRequest(method, uri, version, headers, body)

def to_http_response(response):
	header_section, body = response.split(b"\r\n\r\n")
	header_section_lines = header_section.split(b"\r\n")
	status_line = header_section_lines[0]
	version, status_code, status_message = status_line.rstrip().split(b' ', 2)
	headers = {}
	for i in range(1, len(header_section_lines)):
		key, value = header_section_lines[i].split(b": ")
		headers[key] = value
	return HttpResponse(version, status_code, status_message, headers, body)

def from_http_response(http_response):
	status_line = b' '.join([
		http_response.version,
		http_response.status_code,
		http_response.status_message
	])
	header_section_lines = [status_line]
	for key in http_response.headers:
		value = http_response.headers[key]
		header_section_lines.append(key + b": " + value)
	response = b"\r\n".join(header_section_lines)
	response += b"\r\n\r\n"
	response += http_response.body
	return response

def maybe_gzip(http_request, http_response):
	if b"Accept-Encoding" not in http_request.headers:
		return http_response
	if b"gzip" not in http_request.headers[b"Accept-Encoding"].split(b', '):
		return http_response
	print("gzipping...")
	http_response.body = gzip.compress(http_response.body)
	http_response.headers[b"Content-Encoding"] = b"gzip"
	http_response.headers[b"Content-Length"] = str(len(http_response.body)).encode('ascii')
	return http_response

def maybe_cache(http_request, http_response):
	if http_request.method != b"GET":
		return
	if http_response.status_code != b"200":
		return
	if b"Cache-control" not in http_response.headers:
		return
	cache_control = http_response.headers[b"Cache-control"]
	match = re.search(r"max-age=(\d+)", cache_control.decode("ascii"))
	if not match:
		return
	age = int(match.group(1))
	print(f"Caching {http_request.uri} for {age} seconds")
	CACHE[http_request.uri] = (
		http_response,
		datetime.datetime.now() + datetime.timedelta(seconds=age)
	)

def maybe_return_from_cache(http_request):
	if http_request.uri not in CACHE:
		return
	cached_http_response, expires = CACHE[http_request.uri]
	if expires <= datetime.datetime.now():
		del CACHE[http_request.uri]
		return
	print("Returning cached response")
	return cached_http_response

def main():
	proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	proxy_socket.setblocking(False)
	proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	proxy_socket.bind(("127.0.0.1", 8000))
	proxy_socket.listen(1)

	rlist = [proxy_socket]
	client_socket_to_state = {}
	while True:  # event loop
		readable, _, _ = select.select(rlist, [], [])

		for s in readable:
			if s is proxy_socket:
				client_socket, (client_host, client_port) = proxy_socket.accept()
				client_socket.setblocking(False)
				rlist.append(client_socket)
				continue

			if s not in client_socket_to_state:
				connected = False
				while not connected:
					try:
						upstream_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
						upstream_socket.connect(("127.0.0.1", 9000))
						connected = True
					except:
						time.sleep(1)
				state = State(upstream_socket, b'')
				client_socket_to_state[s] = state
			state = client_socket_to_state[s]

			def execute_one_iteration_of_inner_loop():
				client_message = s.recv(4096)
				if not client_message:
					return True
				state.upstream_socket.send(client_message)
				state.client_request += client_message
				if state.client_request.endswith(b'\r\n\r\n'):
					return True
				return False
			done = execute_one_iteration_of_inner_loop()
			if not done:
				continue

			http_request = None
			if state.client_request:
				http_request = to_http_request(state.client_request)

				http_response = maybe_return_from_cache(http_request)
				if not http_response:
					upstream_response = b''
					while True:
						upstream_message = state.upstream_socket.recv(4096)
						upstream_response += upstream_message
						if not upstream_message:
							break
					http_response = to_http_response(upstream_response)
					
				http_response.headers[b"foo"] = b"bar"
				http_response = maybe_gzip(http_request, http_response)
				maybe_cache(http_request, http_response)
				modified_upstream_response = from_http_response(http_response)
				s.send(modified_upstream_response)

			state.upstream_socket.close()
			del client_socket_to_state[s]

			if (not http_request) or (not should_keep_alive(http_request)):
				s.close()
				rlist.remove(s)

	proxy_socket.close()

if __name__ == "__main__":
	main()
```

### Testing

Sending a request through curl should return a response with "foo: bar" in the headers:

```python
> curl -v localhost:8000
*   Trying 127.0.0.1:8000...
* Connected to localhost (127.0.0.1) port 8000 (#0)
> GET / HTTP/1.1
> Host: localhost:8000
> User-Agent: curl/8.1.1
> Accept: */*
> 
* HTTP 1.0, assume close after body
< HTTP/1.0 200 OK
< Server: SimpleHTTP/0.6 Python/3.11.3
< Date: Thu, 20 Jun 2024 00:55:01 GMT
< Content-type: text/html
< Content-Length: 33
< Last-Modified: Sun, 16 Jun 2024 15:18:48 GMT
< foo: bar
< 
<html><body>Hello!</body></html>
* Closing connection 0
```

If we use Chrome as the client, then the proxy server should print out that it's gzipping.

To test caching, bring down the Python HTTP server and start a netcat session:

```bash
nc -l 9000
```

Then curl. We should see the following in the netcat session:

```bash
GET / HTTP/1.1
Host: localhost:8000
User-Agent: curl/8.1.1
Accept: */*

```

The curl client will be waiting on a response from the server.

We can type in the response we want to return in the netcat session:

```bash
HTTP/1.1 200 OK^M           
Cache-control: max-age=10000^M
Content-length: 6^M
^M
yoyoyo
^C
```

We then should see curl return "yoyoyo". 

Now we can start the Python HTTP server again.

If we curl again, we should see the cached "yoyoyo" response instead of the usual response from the upstream server.

## Sources

* https://csprimer.com/watch/proxy-basic
* https://csprimer.com/watch/proxy-keepalive
* https://csprimer.com/watch/proxy-concurrency
* https://csprimer.com/watch/proxy-features