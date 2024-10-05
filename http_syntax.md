# HTTP syntax

In this post, we describe the syntax of HTTP/1.1.

A client sends request messages to a server.

Each request message starts with a request line, which consists of a "case-sensitive request method, a space, the requested URL, another space, the protocol version, a carriage return and a line feed", e.g.,

```
GET /images/logo.png HTTP/1.1\r\n
```

The GET request method "requests that the target resource transfer a representation of its state." The POST request method "requests that the target resource process the representation enclosed in the request according to the semantics of the target resource." See other methods in the "Request methods" section [here](https://en.wikipedia.org/wiki/HTTP).

After the request line, there are 1 or more request header fields (the `Host: hostname` request header field is required).

Each request header field consists of "the case-insensitive field name, a colon, optional leading whitespace, the field value an optional trailing whitespace and ending with a carriage return and a line feed", e.g.,

```
Host: www.example.com
Accept-Language: en
```

After the request header fields, there is an empty consisting of a carriage return and a line feed.

After the empty line, there is an optional message body.

The server sends response messages to the client.

Each response message starts with a response line, which consists of "the protocol version, a space, the response status code, another space, a possibly empty reason phrase, a carriage return and a line feed", e.g.,

```
HTTP/1.1 200 OK
```

For example, the status code 2xx is a successful request, the status code 4xx is a client error and the status code 5xx is a server error. See other status codes in the "Response status codes" section [here](https://en.wikipedia.org/wiki/HTTP).

After the status line, there are 0 or more response header fields.

Each response header field consists of "the case-insensitive field name, a colon, optional leading whitespace, the field value, an optional trailing whitespace and ending with a carriage return and a line feed", e.g.,

```
Content-Type: text/html
```

After the response header fields, there is an empty consisting of a carriage return and a line feed.

After the empty line, there is an optional message body.

## Sources

* https://en.wikipedia.org/wiki/HTTP