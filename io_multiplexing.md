# I/O multiplexing

I/O multiplexing, or asynchronous I/O, is "the capability to tell the kernel that we want to be notified if one or more I/O conditions are ready (i.e., input is ready to be read, or the descriptor is capable of taking more output)" (UNIX Network Programming Volume 1, Third Edition).

I/O multiplexing is enabled via system calls like select. We can call the select system call in Python via the select module. Here is the select interface in Python (https://docs.python.org/3/library/select.html):

```python
# Inputs:
# * rlist: an iterable of "either integers representing file descriptors
#   or objects with a parameterless method named fileno() returning such
#   an integer" to wait on until one is ready to read
# * wlist: like wlist, but waiting until one is ready to write
# * xlist: like xlist, but waiting until one has an "exceptional condition"
#
# Outputs:
# "The return value is a triple of lists of objects that are ready: 
# subsets of the first three arguments. When the time-out is reached without a
# file descriptor becoming ready, three empty lists are returned."
readable, writable, exceptional = select.select(rlist, wlist, xlist)
```

The select interface in Python is very similar to the select system call interface.

asyncio is an example of a library in Python that uses mechanisms like select under the hood for I/O multiplexing. However, it provides a higher-level interface for concurrent programs that consist of coroutines, or functions that can suspend and resume execution. It is a very lightweight form of concurrency since it operates in a single thread rather than having to spawn multiple processes or multiple threads within a process. nginx uses a combination of threads (1 for each CPU core for parallelism) and I/O multiplexing to serve multiple clients concurrently.

To illustrate the benefits of I/O multiplexing, suppose we have a web server in `server.py` that just responds to a request with a 200 status code:

```python
import socket

def main():
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.bind(("127.0.0.1", 8000))
	server_socket.listen(10)
	while True:
		client_socket, (client_host, client_port) = server_socket.accept()
		message = client_socket.recv(4096)
		if message:
			client_socket.send(b"HTTP/1.0 200 OK\r\n\r\n200 OK")
		client_socket.close()
	server_socket.close()

if __name__ == "__main__":
	main()
```

Start the server:

```bash
> python server.py
```

Send a request using a netcat client:

```bash
> nc localhost 8000
GET / HTTP/1.0

```

We get back the following response:

```bash
HTTP/1.0 200 OK

200 OK  
```

To test the concurrency, open 3 tabs:

In tab 1:

```bash
> python server.py
```

In tab 2:

```bash
> nc localhost 8000
```

In tab 3:

```bash
> nc localhost 8000
GET / HTTP/1.0

```

We do not get back a response this time, because the server has already connected to the client in the second tab and cannot accept another connection.

We now modify the server code to use I/O multiplexing:

```python
import socket
import select

def main():
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# Disable blocking. select will let us know when the server socket is
	# ready to accept a new connection.
	server_socket.setblocking(False)
	server_socket.bind(("127.0.0.1", 8000))
	server_socket.listen(10)

	rlist = [server_socket]
	wlist = []

	while True:  # event loop
		readable, writable, _ = select.select(rlist, wlist, [])

		for s in readable:
			if s is server_socket:
				client_socket, (client_host, client_port) = s.accept()
				# Disable blocking. select will let us know
				# when the client socket is ready for reading or writing.
				client_socket.setblocking(False)
				rlist.append(client_socket)
			else:
				message = s.recv(4096)
				if message:
					wlist.append(s)
				else:
					s.close()
				rlist.remove(s)

		for s in writable:
			if s in wlist:
				wlist.remove(s)
				s.send(b"HTTP/1.0 200 OK\r\n\r\n200 OK")
				s.close()

	server_socket.close()

if __name__ == "__main__":
	main()
```

If we walk through the steps of our concurrency test again, we get a response when we send the request in the 3rd tab.

## Sources

* https://csprimer.com/watch/proxy-concurrency/