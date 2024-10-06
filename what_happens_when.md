# What happens when ...

What happens when you type wikipedia.org into your browser's address box and press enter?

wikipedia.org is a domain name. A **domain name** is a human-readable string that maps to an IP address. It's easier to remember a domain name than an IP address. An **IP address** is a numerical label that identifies a computer on a network. An IP address is organized hierarchically to help route data through the Internet. The browser first has to determine the IP address that wikipedia.org maps to. It does so via a Domain Name System (DNS) lookup. **DNS** is a service that can take a domain name as input and return an IP address for that domain name. The operating system typically stores the IP address of a DNS server. By convention, DNS requests go to port 53. A **port** is a number that the operating system uses to identify a specific process on a computer to direct data to. The browser sends the lookup request to port 53 on this DNS server.

The DNS lookup request uses the **DNS protocol**. A DNS protocol is an example of an **Application Layer** protocol. Another example of an Application Layer protocol is **HTTP**. The DNS protocol is defined by [Request For Comments (RFC) 1035](https://web.archive.org/web/20241005183541/https://www.ietf.org/rfc/rfc1035.txt). See Section 4.1.2 of that RFC for the format of the domain name to send to the DNS server. The browser constructs a binary string conforming to the DNS protocol (DNS is a binary protocol).

To send the DNS request, the browser opens a **socket**, i.e., an interface that the operating system provides for sending and receiving data between computers. Opening a socket requires specifying a communication protocol. For DNS, the browser uses the **User Datagram Protocol (UDP)** communication protocol. The UDP protocol is a **Transport Layer** protocol. Other examples of Transport Layer protocols include **Transmission Control Protocol (TCP)** and **QUIC (Quick UDP Internet Connections)**. See the format of the UDP header in the "UDP datagram structure" section [here](https://web.archive.org/web/20241005183553/https://en.wikipedia.org/wiki/User_Datagram_Protocol). The UDP header contains the source port and the destination port. The operating system prepends this UDP header to the DNS query that the browser constructed.

Opening a socket also requires specifying an address family. The browser uses **IPv4** (**IPv6** is a newer address family with more addresses). IPv4 and IPv6 are examples of **Network Layer** protocols. See the format of the IPv4 header in the "IPv4 header format" [here](https://web.archive.org/web/20241005183612/https://en.wikipedia.org/wiki/IPv4). The IPv4 header contains the source IP address and the destination IP address. The operating system prepends this IPv4 header to the UDP header.

Suppose the computer is connected to an Ethernet cable. The operating system passes the request with the IPv4 header, the UDP header and the DNS query to the computer's **Network Interface Card (NIC)**. The NIC adds the **Ethernet frame** to the request. In particular, it prepends a header and appends a footer. Ethernet is an example of a **Data link layer** protocol. Other examples of data link layer protocols include WiFi and Bluetooth. See the format of the Ethernet frame in the "Structure" section [here](https://web.archive.org/web/20241005183648/https://en.wikipedia.org/wiki/Ethernet_frame). The footer contains a checksum. The header contains a source and destination MAC address. While the IP address can change, the **MAC address** is a unique identifier baked into the Network Interface Controller (NIC). To find the destination MAC address for the Ethernet frame header, the operating system makes an **Address Resolution Protocol (ARP)** request that contains the source IP address, the source MAC address and the destination IP address. This request may be resolved via a cache on the computer or by sending the request over the network (see the example described [here](https://web.archive.org/web/20241006173321/https://en.wikipedia.org/wiki/Address_Resolution_Protocol#Example)).

The request ends up looking like:

```
Ethernet header (source and destination MAC addresses)
IP header (source and destination IP addresses)
UDP header (source and destination ports)
DNS query (wikipedia.org A IN)
Ethernet footer (CRC to check corrupt data)
```

As an aside, the layers discussed above are layers in the [OSI model](https://en.wikipedia.org/wiki/OSI_model). The OSI model was an attempt to develop a new protocol for the internet, but the internet we ended up with does not have a layer 5 or layer 6. This layer abstraction is also leaky. For example, QUIC has the responsibility of a transport layer protocol, but it's implemented at the application layer and uses UDP.

To see a DNS request in action, we can use the `dig` command (the browser may not actually make a DNS request, because it maintains a cache from domain names to IP addresses). First, open WireShark. Then, click the shark icon in the top left corner to start recording traffic. Type `ip.dst == 8.8.8.8` in the command box to filter the traffic. Run  `dig @8.8.8.8 wikipedia.org`. The request should then appear in WireShark.

This post just describes the creation of the UDP packet at a high-level. It does not describe how that packet gets routed through the Internet. It also does not describe how the packet gets received by the DNS server. It also does not describe what happens when the browser gets the IP address for wikipedia.org. In particular, it does not describe how a TCP connection gets established nor how the HTTP request gets sent.

## Sources

* https://github.com/alex/what-happens-when
* https://csprimer.com/watch/what-happens-when/
* https://www.khanacademy.org/computing/computers-and-internet/
* https://csprimer.com/watch/layers/



