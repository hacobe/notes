"""Implement traceroute.

```bash
sudo python traceroute.py wikipedia.org
```

Sources:
* https://csprimer.com/watch/traceroute/
* https://csprimer.com/watch/traceroute-asn/
* https://csprimer.com/watch/traceroute-icmp/
* https://csprimer.com/watch/traceroute-fun/
"""
import socket
import struct
import sys
import time

def internet_checksum(bs):
	total = 0
	for i in range(0, len(bs), 2):
		total += (bs[i] << 8) + bs[i+1]
		total = (total & 0xffff) + (total >> 16)
	return ~total & 0xffff

def create_icmp_message():
	# Prepare outbound ICMP message (Echo request).
	outbound_rtype = 8
	outbound_rcode = 0
	outbound_checksum = 0
	# https://www.rfc-editor.org/rfc/rfc792
	# has the structure of the rest of the header
	outbound_identifier = 123
	outbound_seq_num = 0
	outbound_icmp_message = struct.pack(
		"!BBHHH",
		outbound_rtype,
		outbound_rcode,
		outbound_checksum,
		outbound_identifier,
		outbound_seq_num)
	outbound_checksum = internet_checksum(outbound_icmp_message)
	# Pack it again with the correct checksum.
	outbound_icmp_message = struct.pack(
		"!BBHHH",
		outbound_rtype,
		outbound_rcode,
		outbound_checksum,
		outbound_identifier,
		outbound_seq_num)
	return outbound_icmp_message

def main(dest_ip):
	icmp_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
	icmp_socket.settimeout(1)

	trace_ips = []
	for ttl in range(1, 65):
		icmp_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
		
		outbound_icmp_message = create_icmp_message()

		# ICMP does not have the concept of ports (a transport layer concept).
		icmp_socket.sendto(outbound_icmp_message, (dest_ip, 0))

		# Parse inbound message.
		try:
			inbound_message, (sender_ip, _) = icmp_socket.recvfrom(4096)
		except socket.timeout:
			print(ttl, "*")
			continue

		# It starts with IPv4 header.
		mask = 0x0f  # 0b1111 == 0b00001111
		ihl = inbound_message[0] & mask
		start = ihl * 4

		# After the IPv4 header, there is the ICMP message.
		inbound_rtype = inbound_message[start]

		# 0 = Echo Reply
		# 3 = Destination Unreachable
		# 11 = Time exceeded
		assert inbound_rtype in [0, 3, 11]

		# https://www.rfc-editor.org/rfc/rfc792
		if inbound_rtype == 0:
			inbound_identifier = int.from_bytes(
				inbound_message[start + 4:start + 6], "big")
		else:
			# Haven't tested this for 3, but works for 11 and
			# they should have the same format.

			ihl = inbound_message[start + 8] & mask
			nbytes_ipv4_header = ihl * 4
			nbytes_source_ip = 4
			nbytes_dest_ip = 4
			nbytes_rtype = 1
			nbytes_rcode = 1
			nbytes_checksum = 2
			nbytes_skip = sum([
				nbytes_ipv4_header,
				nbytes_source_ip,
				nbytes_dest_ip,
				nbytes_rtype,
				nbytes_rcode,
				nbytes_checksum,
			])
			inbound_identifier = int.from_bytes(inbound_message[
				start + nbytes_skip:start + nbytes_skip + 2
			], "big")

		print(ttl, sender_ip, inbound_rtype, inbound_identifier)

		trace_ips.append(sender_ip)

		if inbound_rtype in [0, 3]:
			break

	return trace_ips

if __name__ == "__main__":
	assert len(sys.argv) == 2
	dest_ip = sys.argv[1]
	trace_ips = main(dest_ip)

