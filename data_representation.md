# Data representation

A computer stores information in its memory as a sequence of bits, where each byte, or group of 8 bits, has a unique address. A program interprets these bits based on some convention.

For example, a program may interpret a byte $b_7 b_6 \dots b_0$ as a non-negative, or unsigned, integer $n$, where $n = \sum_{i=0}^{7} b_i 2^i$. In this way, a program interprets 00000000 as 0, 00000001 as 1 and so on up to 11111111 as 255.

Similarly, a program may interpret multiple bytes as an unsigned integer (e.g., 4 bytes as a 32-bit, unsigned integer). The order in which a computer stores bytes, or endianness, depends on the computer's architecture. A little-endian architecture stores the least significant byte at the smallest memory address and the most significant byte at the largest memory address. A big-endian architecture does the opposite. The x86 architecture uses little-endian. In contrast, a computer typically transmits bytes over a network using big-endian (e.g., as in the TCP/IP protocol).

Alternatively, a program may interpret a byte as an integer, or signed integer, which can be negative or non-negative, using Two's complement, which is the same as the convention for unsigned integers except that the most significant bit is worth the negative of the value it would have for unsigned integers. Under Two's complement, the 8-bit, signed integer $n = (\sum_{i=0}^{6} b_i 2^i) - b_7 2^7$. In this way, a program interprets 10000000 as -128, 10000001 as -127 and so on up to 11111111 as -1 for negative numbers. And it interprets 00000000 as 0, 00000001 as 1 and so on up to 01111111 as 127 for non-negative numbers. Similarly, a program may interpret multiple bytes as a signed integer (e.g., 4 bytes as a 32-bit, signed integer).

A program may also interpret a byte as a character in the Extended ASCII character set. Extended ASCII maps each character in a 256 character set to an 8-bit, unsigned integer. It is a superset of ASCII, which maps each character in a 128 character set to a 7-bit, unsigned integer. In this way, a program interprets 01100001 as `a` (Extended ASCII maps the character `a` to 97) or 01101000 01100101 01101100 01101100 01101111 as `hello` (spaces added for readability). In a C program that defines a string literal like "hello", the compiler adds a NULL byte to mark the end of the string as in 01101000 01100101 01101100 01101100 01101111 00000000.

Extended ASCII only includes a small number of characters. Unicode is a standard with about 150K characters (as of version 16.0). Unicode maps each character in its character set to a number (called a "code point") in the range [0, 1114111] (called the "codespace"). ASCII characters map to the same values that they do in the ASCII standard. There are different standards for encoding code points as bytes. For example, UTF-8 is variable length encoding of code points to between 1 and 4 bytes (inclusive). Some of the bits in the UTF-8 encoding provide metadata on the number of bytes to use for the code point. For example, UTF-8 encodes the Unicode code point 9731 (the "Snowman") as 10000011 10011000 11100010.

A program may interpret 4 bytes as a single precision (i.e., 32 bit) floating point according to the IEEE 754 standard. The standard decomposes 32 bits as follows:
* sign $s$ (1 bit)
* exponent $x_7 x_6 \dots x_0$ (8 bits), where $x = \sum_{i=0}^7 x_i 2^i$ 
* fraction $f_{22} f_{21} \dots f_0$ (23 bits), where $f = \sum_{i=0}^{22} f_i 2^i$

The value is computed as $(-1)^s \times 2^{x - 127} \times \left(1 + \sum_{i=0}^{22} f_i 2^{-i-1} \right)$ except if $x = 0$ or $x = 255$. If $x = 0$ or $x = 255$, then the value is determined according to the following table:

|s|x|f|value|
|-|-|-|-----|
|0|255|=0|Infinity|
|1|255|=0|-Infinity|
|0|255|!=0|NaN|
|1|255|!=0|NaN|
|0|0|=0|0|
|1|0|=0|-0|
|0|0|!=0|$2^{-126} \times \sum_{i=0}^{22} f_i 2^{-i-1}$|
|1|0|!=0|$-2^{-126} \times \sum_{i=0}^{22} f_i 2^{-i-1}$|

The IEEE 754 standard also defines other floating point formats with varying numbers of byte and levels of precision (e.g., 8 bytes for double precision).