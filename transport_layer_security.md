# Transport Layer Security (TLS)

This post provides a very high-level overview of the **Transport Layer Security** (TLS) protocol as well as explanations of some concepts needed to understand TLS.

## Overview

TLS is "a cryptographic protocol designed to provide communications security over a computer network" (https://en.wikipedia.org/wiki/Transport_Layer_Security).

The client and the server first establish a TCP connection. The client presents a maximum TLS version and a list of cipher suites it supports. A cipher suite specifies a set of algorithms to use. For example, the cipher suite TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256 specifies using Elliptic Curve Diffie-Hellman Ephemeral (ECDHE) for the key exchange, RSA for authentication, AES with a key size of 128 in Galois Counter Mode for encryption, and SHA256 for hashing.

The server chooses a TLS version and a cipher suite and communicates its choices to the client.

The server provides its public-key certificate. The certificate includes the server name, the server's public key and a digital signature from a Certificate Authority. The client uses the certificate to authenticate the server.

The client and the server perform a public key exchange in order to create a shared private key, which they then use for symmetric encryption and decryption. In the public key exchange, the server includes a digital signature created using the server's private key, which the client validates using the server's public key from the certificate.

## Public-key cryptography

In symmetric cryptography, Alice and Bob share a secret key. Alice uses the secret key to encrypt a message and sends it to Bob. Bob receives the message from Alice and uses the secret key to decrypt it. If an adversary intercepts the message, they can't read it, because the message is encrypted. For example, Alice and Bob could use a [Caesar cipher](https://en.wikipedia.org/wiki/Caesar_cipher), where the number of rotations of the alphabet is the secret key. The problem is that Alice and Bob need to agree on a secret key before they start sending messages. Maybe they meet clandestinely in a park.

In asymmetric cryptography, or public-key cryptography, Alice generates a pair of keys in such a way that if she encrypts a message with one key, then it can only be decrypted with the other key and vice versa (we will not explain how she does this, but assume that she can). She keeps one of the keys in the pair private (call it the private key) and the other key in the pair public (call it the public key). She shares the public key widely. Bob does the same thing to create his own private key and public key.

Alice can then send a message to Bob by encrypting the message with Bob's public key. Only Bob can read the message, because only Bob has his private key. They do not need to meet in a park to agree on a secret key.

Alice can also prove to Bob that she sent the message by encrypting a message with her private key. If Bob can decrypt the message with Alice's public key, then he knows that Alice sent the message.

An example of a public-key cryptosystem is [RSA](https://en.wikipedia.org/wiki/RSA_(cryptosystem)).

## Diffie-Hellman key exchange

Public-key cryptography is slow compared to symmetric encryption, so we do not encrypt most messages sent over the internet using public-key cryptography. Instead, we use public-key cryptography to agree on a secret key and then use a symmetric cryptosystem like [AES](https://en.wikipedia.org/wiki/Advanced_Encryption_Standard).

Diffie-Hellman key exchange is a protocol for constructing a shared secret key.

In the public domain, we have a generator. Alice uses the generator (G) and her private key (A) to create a public key (AG). Bob uses the generator (G) and his private key (B) to create a public key (BG). Alice and Bob exchange their public keys. Alice uses her private key (A) and Bob's public key (BG) to construct the secret key (ABG). Bob uses his private key (B) and Alice's public key (AG) to construct the secret key (ABG). Now, each party has the same secret key.

## Digital signatures

Alice has a document that she wants to send to Bob and she wants to prove to Bob that she sent it. Alice can encrypt the document with her private key to create a signature. She can then send a message to Bob that includes the document and the signature. Bob can decrypt the signature with Alice's public key. If the decrypted signature and the document matches, then Bob knows that Alice sent the message.

The problem with this protocol is that the document could be very short, which would make the encryption easy to break, or very long, which would make the encryption computationally intensive. Instead of encrypting the document, Alice first hashes the document and potentially pads the hash. The padded hash is neither too small nor too large. She then encrypts the padded hash with her private key to create the signature. Bob then follows the same procedure to create a padded hash from the document. He decrypts the signature and checks that it matches the padded hash.

## Certificates

In Diffie-Hellman key exchange, the client and the server exchange public keys. But what happens if an adversary intercepts the server's message in the exchange and modifies it to replace the server's public key with its own public key (i.e., a **man-in-the-middle attack**)? A **public-key certificate** is a document that includes a public key, information about the owner of the public key and a signature created with the private key of a certificate issuer that has verified the document. The server can obtain a certificate from a certificate issuer verifying that the server indeed owns the public key it claims to. The server can then include the certificate in its message to the client. The client can then validate the certificate from the certificate issuer with the certificate issuer's public key. How does the client know the certificate issuer's public key? Typically, an operating system and/or a browser comes with certificates (**root certificates**) from a few trusted certificate issuers (**Certificate Authorities**).

## Resources

* [TLS Handshake Explained - Computerphile](https://www.youtube.com/watch?v=86cQJ0MMses&t=322s)
* [Public Key Cryptography - Computerphile](https://www.youtube.com/watch?v=GSIDS_lvRv4)
* [Secret Key Exchange (Diffie-Hellman) - Computerphile](https://www.youtube.com/watch?v=NmM9HA2MQGI)
* [What are Digital Signatures? - Computerphile](https://www.youtube.com/watch?v=s22eJ1eVLTU&t=309s)
* https://en.wikipedia.org/wiki/Man-in-the-middle_attack
* https://en.wikipedia.org/wiki/Certificate_authority
* https://en.wikipedia.org/wiki/Public_key_certificate
* https://en.wikipedia.org/wiki/Root_certificate
* https://security.stackexchange.com/questions/20803/how-does-ssl-tls-work/20833#20833
* https://web.archive.org/web/20240102054702/https://letsencrypt.org/how-it-works/







