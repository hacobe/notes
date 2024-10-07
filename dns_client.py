"""Implement a DNS client.

# Requirements

The goal is to implement a DNS client like `dig` that can support:
* A, AAAA, NS, PTR, CNAME, SOA, MX or TXT record types
* reverse DNS queries using the -x flag, where we supply an IP address
  and it returns a domain name.
* DNS trace using the +trace flag, where we supply a domain name and
  it returns the root servers, the top-level domain servers,
  the name servers and the IP address.
* sending requests to a particular domain name or IP address using
  the syntax @[domain name] or @[ip address].

Refer to RFC1035 for all record types except AAAA. Refer to RFC3596 for AAAA.

The client should use EDNS(0) (RFC6891) to increase the maximum message size from
512 to 4096 bytes.

The client should parse the Answer (resorce records answering the question),
Authority (resource records pointing toward an authoritative name server) and
Additional (resource records holding additional information that relates but
to the query but does not necessarily answer the question).

The output format should be name, TTL, class, type and rdata.

# Examples

The examples are using dig, but just replace "dig" with "python dns_client.py" to
test dns_client.py.

```bash
> dig @8.8.8.8 google.com
;; ANSWER SECTION:
google.com.		23	IN	A	172.217.164.110

> dig @8.8.8.8 google.com A
;; ANSWER SECTION:
google.com.		128	IN	A	142.251.214.142

> dig @8.8.8.8 google.com AAAA
;; ANSWER SECTION:
google.com.		69	IN	AAAA	2607:f8b0:4005:80d::200e

> dig @8.8.8.8 google.com NS
;; ANSWER SECTION:
google.com.		4373	IN	NS	ns3.google.com.
google.com.		4373	IN	NS	ns1.google.com.
google.com.		4373	IN	NS	ns4.google.com.
google.com.		4373	IN	NS	ns2.google.com.

> dig @8.8.8.8 238.211.251.142.in-addr.arpa PTR
;; ANSWER SECTION:
238.211.251.142.in-addr.arpa. 925 IN	PTR	sea30s13-in-f14.1e100.net.

> dig @8.8.8.8 google.com CNAME
;; AUTHORITY SECTION:
google.com.		52	IN	SOA	ns1.google.com. dns-admin.google.com. 652024044 900 900 1800 60

> dig @8.8.8.8 gmail.com MX
;; ANSWER SECTION:
gmail.com.		2968	IN	MX	5 gmail-smtp-in.l.google.com.
gmail.com.		2968	IN	MX	30 alt3.gmail-smtp-in.l.google.com.
gmail.com.		2968	IN	MX	20 alt2.gmail-smtp-in.l.google.com.
gmail.com.		2968	IN	MX	10 alt1.gmail-smtp-in.l.google.com.
gmail.com.		2968	IN	MX	40 alt4.gmail-smtp-in.l.google.com.

> dig @8.8.8.8 google.com TXT
;; ANSWER SECTION:
google.com.		2418	IN	TXT	"v=spf1 include:_spf.google.com ~all"
google.com.		2418	IN	TXT	"facebook-domain-verification=22rm551cu4k0ab0bxsw536tlds4h95"
google.com.		2418	IN	TXT	"docusign=05958488-4752-4ef2-95eb-aa7ba8a3bd0e"
google.com.		2418	IN	TXT	"onetrust-domain-verification=de01ed21f2fa4d8781cbc3ffb89cf4ef"
google.com.		2418	IN	TXT	"globalsign-smime-dv=CDYX+XFHUw2wml6/Gb8+59BsH31KzUr6c1l2BPvqKX8="
google.com.		2418	IN	TXT	"google-site-verification=wD8N7i1JTNTkezJ49swvWW48f8_9xveREV4oB-0Hf5o"
google.com.		2418	IN	TXT	"MS=E4A68B9AB2BB9670BCE15412F62916164C0B20BB"
google.com.		2418	IN	TXT	"cisco-ci-domain-verification=479146de172eb01ddee38b1a455ab9e8bb51542ddd7f1fa298557dfa7b22d963"
google.com.		2418	IN	TXT	"google-site-verification=TV9-DBe4R80X4v0M4U_bd_J9cpOJM0nikft0jAgjmsQ"
google.com.		2418	IN	TXT	"docusign=1b0a6754-49b1-4db5-8540-d2c12664b289"
google.com.		2418	IN	TXT	"apple-domain-verification=30afIBcvSuDV2PLX"

> dig @8.8.8.8 google.com SOA
;; ANSWER SECTION:
google.com.		40	IN	SOA	ns1.google.com. dns-admin.google.com. 652024044 900 900 1800 60

> dig @8.8.8.8 -x 142.251.211.238
;; ANSWER SECTION:
238.211.251.142.in-addr.arpa. 469 IN	PTR	sea30s13-in-f14.1e100.net.

> dig +trace wikipedia.org
.			513448	IN	NS	d.root-servers.net.
.			513448	IN	NS	e.root-servers.net.
.			513448	IN	NS	f.root-servers.net.
.			513448	IN	NS	g.root-servers.net.
.			513448	IN	NS	h.root-servers.net.
.			513448	IN	NS	i.root-servers.net.
.			513448	IN	NS	j.root-servers.net.
.			513448	IN	NS	k.root-servers.net.
.			513448	IN	NS	l.root-servers.net.
.			513448	IN	NS	m.root-servers.net.
.			513448	IN	NS	a.root-servers.net.
.			513448	IN	NS	b.root-servers.net.
.			513448	IN	NS	c.root-servers.net.
.			513448	IN	RRSIG	NS 8 0 518400 20240727050000 20240714040000 20038 . JcMg6fjj2Rp2Wqp2aC0M8J61gRIv3xRLSo+QtR5SI/CRV+p+HP2N0uq6 VkO2286+wt3ZCHA3MDfTP3hfg6OMDlDLKlnxB7xELI7d+hChpJRfyv0m CvmwchpMYcm5ThtHrQLFwFUkFAbajCJFG84uVBX8HKOBhB9a8P2dfUOs Rpu+Ln4QQjmV0B4aF8+bE6S3jv0dG3kSE3H8YdBvdc4zSxrz9VlfkeaO oeALVwp04fQNqfWH7FHHtMKEaRu+AlL+zgZ6QZWXhkrsscf3Mw3ZK6zo xEGE5cq608TpOKEWpACMnmecQTxTbhN0XeNt2co7ouVsz7qih02HJ17C NvXFVQ==
;; Received 1097 bytes from 75.75.75.75#53(75.75.75.75) in 108 ms

org.			172800	IN	NS	a2.org.afilias-nst.info.
org.			172800	IN	NS	b2.org.afilias-nst.org.
org.			172800	IN	NS	d0.org.afilias-nst.org.
org.			172800	IN	NS	a0.org.afilias-nst.info.
org.			172800	IN	NS	b0.org.afilias-nst.org.
org.			172800	IN	NS	c0.org.afilias-nst.info.
org.			86400	IN	DS	26974 8 2 4FEDE294C53F438A158C41D39489CD78A86BEB0D8A0AEAFF14745C0D 16E1DE32
org.			86400	IN	RRSIG	DS 8 1 86400 20240727050000 20240714040000 20038 . ASBqyv3RHDMfu1QLk1ki+KiSqAiu51we68RdfWTnnQyBLpb8/bs4mvqX hBoZywBN07euCytcdfQlCAXIFAGGmjjO0Ks0sJ6aNYTa8Bf0moHzh0Ir 3MoUCHLQiAgSv1ARgi7l4o8vBLZV/EyIvUqut3FLTElkg2vxcR2P539V GA6N+4EBnLljONu9Fk3yo3j1REfwJDTm4u/QgUEbpC0Q5aZGOEwZ7bxF kFxmQXWtJmKUkXHu1VJ4fV4tzaZn/HKrMN4e9S4Uof3oJiB07cvJ4hqh gyK+YDy7IzaMbc7XceS+FGvtiRz8AvYOnE1p6iOIxQMSTNSGUtamh6o5 COr+/w==
;; Received 779 bytes from 198.41.0.4#53(a.root-servers.net) in 30 ms

wikipedia.org.		3600	IN	NS	ns1.wikimedia.org.
wikipedia.org.		3600	IN	NS	ns0.wikimedia.org.
wikipedia.org.		3600	IN	NS	ns2.wikimedia.org.
gdtpongmpok61u9lvnipqor8lra9l4t0.org. 3600 IN NSEC3 1 1 0 332539EE7F95C32A GDTREA8KMJ2RNEQEN4M2OGJ26KFSUKJ7  NS SOA RRSIG DNSKEY NSEC3PARAM
gdtpongmpok61u9lvnipqor8lra9l4t0.org. 3600 IN RRSIG NSEC3 8 2 3600 20240804175500 20240714165500 36783 org. Canmla6Vc09eIampe/w+Y/JnzRMryPvMUUweI9uhDu46DLIKVHvs3U4f 7xauUfZTp4dSVSLl/szpV3A7py/IPrYEdV3m76WS3CO4m7xytIt/yZxw 0MxdJpF2gxQfJB7H9cyLztOi/VbKpEEO6xAQ/6ezOMHFSnGnyuDMFDkW wCQ=
tpeahq77pcfqu9h00c3mh570ah1f4g65.org. 3600 IN NSEC3 1 1 0 332539EE7F95C32A TPEGNJF8A7B81F9A0UHNBFFJOTS0K51A  NS DS RRSIG
tpeahq77pcfqu9h00c3mh570ah1f4g65.org. 3600 IN RRSIG NSEC3 8 2 3600 20240730152251 20240709142251 36783 org. ZZdn0nX9i13arkgMVqPGxUQITwLXHhXzZwCt0MK5Lxy4h8Cfq2NJ+u2x FVJE37vWUKIDwTYMJfyUnlL7tMVjaCCifbGwZ82IKowbVl62Z0i5cqSK 3EofkX/Ls54l8M529qcePige0xj9YDUMBV8dWqmeX/lstAM2ML/E5MeK Ikk=
;; Received 655 bytes from 199.19.57.1#53(d0.org.afilias-nst.org) in 124 ms

wikipedia.org.		300	IN	A	198.35.26.96
;; Received 58 bytes from 198.35.27.27#53(ns2.wikimedia.org) in 17 ms
```

It should handle multiple sections:

```
> dig @198.41.0.4 org NS
;; AUTHORITY SECTION:
org.			172800	IN	NS	a2.org.afilias-nst.info.
org.			172800	IN	NS	b2.org.afilias-nst.org.
org.			172800	IN	NS	d0.org.afilias-nst.org.
org.			172800	IN	NS	a0.org.afilias-nst.info.
org.			172800	IN	NS	b0.org.afilias-nst.org.
org.			172800	IN	NS	c0.org.afilias-nst.info.

;; ADDITIONAL SECTION:
a2.org.afilias-nst.info. 172800	IN	A	199.249.112.1
a2.org.afilias-nst.info. 172800	IN	AAAA	2001:500:40::1
b2.org.afilias-nst.org.	172800	IN	A	199.249.120.1
b2.org.afilias-nst.org.	172800	IN	AAAA	2001:500:48::1
d0.org.afilias-nst.org.	172800	IN	A	199.19.57.1
d0.org.afilias-nst.org.	172800	IN	AAAA	2001:500:f::1
a0.org.afilias-nst.info. 172800	IN	A	199.19.56.1
a0.org.afilias-nst.info. 172800	IN	AAAA	2001:500:e::1
b0.org.afilias-nst.org.	172800	IN	A	199.19.54.1
b0.org.afilias-nst.org.	172800	IN	AAAA	2001:500:c::1
c0.org.afilias-nst.info. 172800	IN	A	199.19.53.1
c0.org.afilias-nst.info. 172800	IN	AAAA	2001:500:b::1
```

Also a good test:

```
> dig +trace twitter.com
```

# Sources

* https://csprimer.com/watch/dns-trace/
"""
import collections
import dataclasses
import enum
import socket
import struct
import sys

# a.root-servers.net
_DNS_ROOT_SERVER = "198.41.0.4"

class RecordType(enum.IntEnum):
	A = 1
	NS = 2
	CNAME = 5
	SOA = 6
	PTR = 12
	MX = 15
	TXT = 16
	AAAA = 28
	OPT = 41

@dataclasses.dataclass
class DnsQuery:
	domain_name: str
	record_type: RecordType = RecordType.A
	server: str = "8.8.8.8"

@dataclasses.dataclass
class ResourceRecord:
	name: str
	ttl: int
	rclass: int
	rtype: RecordType
	# key-value pairs for rdata
	rdata: collections.OrderedDict[str, str]
	
	def __str__(self):
		assert self.rclass == 1
		return f"{self.name} {self.ttl} IN {self.rtype.name} {' '.join(self.rdata.values())}"

@dataclasses.dataclass
class Response:
	answer: list[ResourceRecord]
	authority: list[ResourceRecord]
	additional: list[ResourceRecord]

	def __str__(self):
		s = ""

		if self.answer:
			s += "ANSWER\n"
			for rr in self.answer:
				s += str(rr) + "\n"

		if self.authority:
			s += "AUTHORITY\n"
			for rr in self.authority:
				s += str(rr) + "\n"

		if self.additional:
			s += "ADDITIONAL\n"
			for rr in self.additional:
				s += str(rr) + "\n"

		return s

def parse_domain_name(response, start):
	i = start
	labels = []
	end = None
	while True:
		if response[i] == 0:
			if end is None:
				end = i + 1
			break

		mask = 0b11000000
		is_pointer = response[i] & mask
		if is_pointer:
			inverse_mask = 0b00111111
			pointer_parts = [
				(response[i] & inverse_mask).to_bytes(1, "big"),
				(response[i+1]).to_bytes(1, "big"),
			]
			if end is None:
				end = i + 2
			i = int.from_bytes(b"".join(pointer_parts), "big")
			continue

		label = b""
		nbytes = response[i]
		i += 1  # Skip nbytes
		for _ in range(nbytes):
			label += response[i].to_bytes(1, "big")
			i += 1
		labels.append(label.decode("ascii"))

	assert end is not None
	domain_name = ".".join(labels)
	return domain_name, end

def parse_resource_record(response, i):
	name, i = parse_domain_name(response, i)

	rtype, rclass, ttl, rdlength = struct.unpack("!HHIH", response[i:i+10])

	i += 10

	rdata_kvs = []
	unparsed_rdata = response[i:i+rdlength]

	if rtype == RecordType.A:
		ipv4 = ".".join([str(part) for part in unparsed_rdata])
		rdata_kvs.append(("ipv4", ipv4))
	elif rtype == RecordType.AAAA:
		# "IPv6 addresses are represented as eight groups of four hexadecimal digits each, "
		# "separated by colons. The full representation may be shortened; for example, "
		# "2001:0db8:0000:0000:0000:8a2e:0370:7334 becomes 2001:db8::8a2e:370:7334."
		# (https://en.wikipedia.org/wiki/IPv6)
		# Could have also use the ipaddress module in Python.
		assert len(unparsed_rdata) == 16
		ip_parts = []
		for start in range(0, 16, 2):
			end = start + 2
			part = unparsed_rdata[start:end].hex()
			j = 0
			while j < len(part):
				if part[j] != "0":
					break
				j += 1
			ip_parts.append(part[j:])
		new_ip_parts = []
		in_streak = False
		for part in ip_parts:
			if part == "" and (not in_streak):
				in_streak = True
				new_ip_parts.append(part)
			elif part == "" and (in_streak):
				continue
			elif part != "" and (in_streak):
				in_streak = False
				new_ip_parts.append(part)
			else:
				assert part != "" and (not in_streak)
				new_ip_parts.append(part)
		ipv6 = ":".join(new_ip_parts)
		rdata_kvs.append(("ipv6", ipv6))
	elif rtype in [RecordType.NS, RecordType.CNAME, RecordType.PTR]:
		domain_name, _ = parse_domain_name(response, i)
		rdata_kvs.append(("domain_name", domain_name))
	elif rtype == RecordType.MX:
		preference = struct.unpack("!H", response[i:i+2])[0]
		domain_name, _ = parse_domain_name(response, i + 2)
		rdata_kvs.append(("preference", str(preference)))
		rdata_kvs.append(("mx", domain_name))
	elif rtype == RecordType.TXT:
		rdata_kvs.append(("txt", unparsed_rdata.decode("ascii")))
	elif rtype == RecordType.SOA:
		j = i
		mname, j = parse_domain_name(response, j)
		rname, j = parse_domain_name(response, j)
		serial, refresh, retry, expire, minimum = struct.unpack("!IIIII", response[j:j+20])
		rdata_kvs.append(("mname", mname))
		rdata_kvs.append(("rname", rname))
		rdata_kvs.append(("serial", str(serial)))
		rdata_kvs.append(("refresh", str(refresh)))
		rdata_kvs.append(("retry", str(retry)))
		rdata_kvs.append(("expire", str(expire)))
		rdata_kvs.append(("minimum", str(minimum)))
	elif rtype == RecordType.OPT:
		rdata_kvs = None
	else:
		raise ValueError(f"Unrecognized rtype <{RecordType(rtype).name}>")

	if rdata_kvs is None:
		rr = None
	else:
		rdata = collections.OrderedDict(rdata_kvs)
		rr = ResourceRecord(name, ttl, rclass, RecordType(rtype), rdata)

	i += rdlength

	return rr, i

def execute_dns_query(dns_query):
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	xid = 0
	flags = 0x100
	header = struct.pack("!HHHHHH", xid, flags, 1, 0, 0, 1)

	if dns_query.domain_name == ".":
		domain_name_parts = []
	else:
		domain_name_parts = dns_query.domain_name.split(".")

	qname_parts = []
	for part in domain_name_parts:
		part_bytes = part.encode("ascii")
		part_nbytes = len(part_bytes).to_bytes(1, "big")
		qname_parts.append(part_nbytes)
		qname_parts.append(part_bytes)

	qname = b"".join(qname_parts) + b"\x00"
	question = qname + struct.pack("!HH", int(dns_query.record_type), 1)
	# EDNS(0) (https://datatracker.ietf.org/doc/html/rfc6891)
	additional = b"\x00" + struct.pack("!HHIH", 41, 4096, 0, 0)
	request = header + question + additional
	s.sendto(request, (dns_query.server, 53))
	unparsed_response, (sender_ip, sender_port) = s.recvfrom(4096)

	_, _, _, ancount, nscount, arcount = struct.unpack("!HHHHHH", unparsed_response[:12])

	# Skip header.
	i = 12

	# Skip qname.
	while True:
		if unparsed_response[i] == 0:
			break
		i += 1

	# Skip zero byte.
	i += 1

	# Skip qtype and qclass.
	i += 4

	answer = []
	for _ in range(ancount):
		rr, i = parse_resource_record(unparsed_response, i)
		if rr is not None:
			answer.append(rr)

	authority = []
	for _ in range(nscount):
		rr, i = parse_resource_record(unparsed_response, i)
		if rr is not None:
			authority.append(rr)

	additional = []
	for _ in range(arcount):
		rr, i = parse_resource_record(unparsed_response, i)
		if rr is not None:
			additional.append(rr)

	return Response(answer, authority, additional)

def trace(dns_query, level=0): 
	if level == 0:
		assert dns_query.server == _DNS_ROOT_SERVER

	response = execute_dns_query(dns_query)
	print(response)

	if response.answer:
		return response

	if not response.authority:
		return response

	authority = response.authority[0]
	# Look for the IP address in the additional section
	# associated with the first entry of the authority section.
	for add in response.additional:
		if authority.rdata["domain_name"] == add.name and add.rtype == RecordType.A:
			q = DnsQuery(dns_query.domain_name, dns_query.record_type, server=add.rdata["ipv4"])
			return trace(q, level=level+1)

	# If we can't find the IP address in the additional section, then send another
	# request to the root server for the IP address.
	q = DnsQuery(authority.rdata["domain_name"], RecordType.A, server=_DNS_ROOT_SERVER)
	response = trace(q, level=level+1)

	if not response.answer:
		return response

	q = DnsQuery(
		dns_query.domain_name,
		dns_query.record_type,
		server=response.answer[0].rdata["ipv4"])
	return trace(q, level=level+1)

def parse_argv(argv):
	args = sys.argv[1:]

	trace = 0
	reverse = 0
	servers = []
	filtered_args = []
	for arg in args:
		if arg == "-x":
			reverse += 1
			continue
		if arg.startswith("@"):
			servers.append(arg[1:])
			continue
		if arg == "+trace":
			trace += 1
			continue
		filtered_args.append(arg)

	assert len(servers) == 0 or len(servers) == 1
	assert reverse == 0 or reverse == 1
	assert trace == 0 or trace == 1
	assert len(filtered_args) == 1 or len(filtered_args) == 2, filtered_args

	dns_query_args = {}

	if reverse == 1:
		assert len(filtered_args) == 1, filtered_args
		ip_addr = filtered_args[0]
		domain_name = ".".join(ip_addr.split(".")[::-1]) + ".in-addr.arpa"
		dns_query_args["record_type"] = RecordType.PTR
	else:
		domain_name = filtered_args[0]
		if len(filtered_args) == 2:
			dns_query_args["record_type"] = RecordType[filtered_args[1]]

	dns_query_args["domain_name"] = domain_name

	if len(servers) == 1:
		dns_query_args["server"] = servers[0]

	if trace == 1:
		assert len(servers) == 0
		dns_query_args["server"] = _DNS_ROOT_SERVER

	dns_query = DnsQuery(**dns_query_args)
	return dns_query, (trace == 1)

def main(argv):
	dns_query, is_trace = parse_argv(argv)
	if is_trace:
		trace(dns_query)
		return

	response = execute_dns_query(dns_query)
	print(response)
	print(f"SERVER: {dns_query.server}")

if __name__ == "__main__":
	main(sys.argv)

