"""Echo server.

Usage:

```bash
python echo_server.py
# in a separate shell:
nc -u 127.0.0.1 8000  # use netcat with the -u flag for UDP
```

Sources:
* https://csprimer.com/watch/shout-server/
"""
import socket

def main():
	s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
	s.bind(("127.0.0.1", 8000))
	while True:
		buffer_size = 1024
		msg, (ip, port) = s.recvfrom(buffer_size)
		s.sendto(msg, (ip, port))

if __name__ == "__main__":
	main()