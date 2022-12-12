# Encoding and evolution

In a large application, code changes often do not happen immediately, because:
* In server-side applications, we perform a staged rollout to ensure that the new version works before deploying it to all nodes in the network
* In client-side applications, the user chooses when to install an update

For these reasons, old and new versions of the code and old and new data formats may coexist in the system.

We therefore need both:
* "**Backward compatibility**: Newer code can read data that was written by older code."
* "**Forward compatibility**: Older code can read data that was written by newer code."

Programs work with at least 2 representations of data:
* In-memory data structures optimized for efficient access and manipulation by the CPU (uses pointers)
* Self-contained sequence of bytes for writing to a file or sending it over a network (no pointers, because a pointer would not make sense to another process)

The process of converting the in-memory data structures to the sequence of bytes is called **encoding**, serializing or marshalling and the reverse process is called **decoding**, deserializing or unmarshalling.

There are **language-specific formats** like pickle for Python, but it not recommmend to use these, because of:
* it's tied to particular language
* there are security issues from support for decoding an arbitrary byte sequence
* there's little support for schema evolution
* it's inefficient

JSON, XML and CSV are **textual formats**. These also have issues:
* Ambiguity around the encoding of numbers (e.g., JSON doesn't distinguish integers from floating point)
* Support for unicode but not binary strings
* Optional or no schema support
Still, these textual formats are sufficient for many purposes.

Protocol buffers are a **binary encoding format**. Each record takes up 33 bytes. The first 5 bits are the field tag, the next 3 bits are the type, the next 8 bits are the length and the rest of the bits are the data.

How do protocol buffers handle schema evolution?
* Newer code can read data that was written by older code as long as the field tags have the same meaning.
* Older code can read data that was written by newer code, because older code simply ignores field tags that it does not recognize.

Protocol buffers rely on code generation to work with a user's language of choice.

Here are 3 ways that data can flow between processes:
* **via databases**: "one process writes encoded data, and another process reads it again sometime in the future" but no data is sent over a network
* **via service calls**: "one process sends a request over the network to another process and expects a response as quickly as possible"
* **via asynchronous message-passing**: This is somewhere in between databases and service calls. It is similar to data flowing via databases "in that the message is not sent via a direct network connection, but goes via an intermediary called a message broker". It is similar to data flowing via service calls "in that a client's request (usually called a message) is delivered to another process with low latency".

A common arrangement for communicating over a network is to have clients and servers. The servers "expose an API over the network, and the clients can connect to the servers to make requests to that API". The API exposed by the server is called a **service**. (Note that a server can itself be a client to another service). 

Web browsers make GET requests to web servers to download data and POST requests to submit data with an API consisting of a standardized set of protocols and data formats. If the protocol used is HTTP, then the service is called a **web service**.

There are 2 main approaches to web services:
* REST: REST is not a protocol, but a design philosophy that builds on HTTP.
* SOAP: XML-based protocol for making network API requests

All web services are based on the idea of a **remote procedure call (RPC)**, which "tries to make a request to a remote network service look the same as calling a function or method in your programming language, within the same process".

Here are some features of a RPC that make it different from a local procedure call:
* Unpredictability: A network request may be lost due to a network problem or the remote machine being unavailable
* Timeouts: A RPC may return a result, throw an exception or timeout.
* Duplicate calls: If you retry a failed request, then it could have been executed on the remote machine, but the response may have been lost over the network.
* Variable latency
* All parameters need to be encoded
* Possibly a need to translate between different languages

gRPC is an RPC implementation using Protocol Buffers.

Asynchronous message-passing uses an intermediary called a **message broker** (or message queue). The advantages of asynchronous message-passing over direct RPC are that:
* "It can act as a buffer if the recipient is unavailable or overloaded, and thus improve system reliability."
* "It can automatically redeliver messages to a process that has crashed, and thus prevent messages from being lost."
* "It avoids the sender needing to know the IP address and port number of the recipient (which is particularly useful in a cloud deployment where virtual machines often come and go)."
* "It allows one message to be sent to several recipients."
* "It logically decouples the sender from the recipient (the sender just publishes messages and doesn’t care who consumes them)."

In asynchronous message-passing, the sender does not wait for a response from the receiver.

In general, message brokers "are used as follows: one process sends a message to a named queue or topic, and the broker ensures that the message is delivered to one or more consumers of or subscribers to that queue or topic. There can be many producers and many consumers on the same topic."

Note that "a consumer may itself publish messages to another topic...or to a reply queue that is consumed by the sender of the original message".

## Sources

* Chapter 4, DDIA