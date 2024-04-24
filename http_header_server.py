"""HTTP header server.

A TCP server that replies to an HTTP GET request with
a 200 response and the request header as JSON in the body.

Usage:

```bash
python http_header_server.py
# in a separate shell:
curl 127.0.0.1:8000 # sends a GET request
```

Sources:
* https://csprimer.com/watch/http-header-server/
"""
import json
import socket

def main():
	s = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
	s.bind(("127.0.0.1", 8000))
	backlog = 1
	s.listen(backlog)
	while True:
		t, (ip, port) = s.accept()

		# We should actually keep calling recv here, because the HTTP
		# request could be sent over multiple packets.
		request = t.recv(4096)

		# b"GET / HTTP/1.1\r\nHost: 127.0.0.1:8000\r\nUser-Agent: curl/8.1.1\r\nAccept: */*\r\n\r\n"
		print(request)

		lines = request.decode("ascii").strip().split("\r\n")

		# ["GET / HTTP/1.1", "Host: 127.0.0.1:8000", "User-Agent: curl/8.1.1", "Accept: */*"]
		print(lines)

		header_key_to_val = {}
		for line in lines[1:]:
			key, val = line.split(": ")
			header_key_to_val[key] = val

		# {"Host": "127.0.0.1:8000", "User-Agent": "curl/8.1.1", "Accept": "*/*"}
		print(header_key_to_val)

		response_header = b"HTTP/1.1 200 ok"
		response_delimiter = b"\r\n\r\n"
		response_body = json.dumps(header_key_to_val, indent=4).encode("ascii")

		t.send(response_header)
		t.send(response_delimiter)
		t.send(response_body)

		t.close()

if __name__ == "__main__":
	main()
