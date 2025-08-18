# Character encoding in Python

## ASCII

ASCII maps each character in a 128 character set to an integer in the interval [0, 127].

Each ASCII character is one byte, or 8 bits, though it can fit into 7 bits (2^8 = 256 and 2^7 = 128).

```python
>>> [chr(num) for num in range(128)]
['\x00', '\x01', '\x02', '\x03', '\x04', '\x05', '\x06', '\x07', '\x08', '\t', '\n', '\x0b', '\x0c', '\r', '\x0e', '\x0f', '\x10', '\x11', '\x12', '\x13', '\x14', '\x15', '\x16', '\x17', '\x18', '\x19', '\x1a', '\x1b', '\x1c', '\x1d', '\x1e', '\x1f', ' ', '!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ':', ';', '<', '=', '>', '?', '@', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '[', '\\', ']', '^', '_', '`', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '{', '|', '}', '~', '\x7f']
```

A subset of these characters are defined as "printable". Different systems have different definitions of printable. I think there were 95 printable characters in the original ASCII character encoding (the characters associated with the range [32, 126]. However, Python includes '\t', '\n', '\r', '\x0b' and '\x0c' (9, 10, 11, 12 and 13) in its definition of printable characters.

```python
>>> string.printable
'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ \t\n\r\x0b\x0c'

>>> len(string.printable)
100

>>> [ch for ch in string.printable]
['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/', ':', ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`', '{', '|', '}', '~', ' ', '\t', '\n', '\r', '\x0b', '\x0c']

>>> sorted([num for num in bytes(string.printable, "ascii")])
[9, 10, 11, 12, 13, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126]

>>> [chr(num) for num in sorted([num for num in bytes(string.printable, "ascii")])]
['\t', '\n', '\x0b', '\x0c', '\r', ' ', '!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ':', ';', '<', '=', '>', '?', '@', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '[', '\\', ']', '^', '_', '`', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '{', '|', '}', '~']
```

The non-printable characters are control characters: "codes originally intended not to represent printable information, but rather to control devices (such as printers) that make use of ASCII, or to provide meta-information about data streams such as those stored on magnetic tape. For example, character 10 represents the "line feed" function (which causes a printer to advance its paper), and character 8 represents 'backspace'." (https://en.wikipedia.org/wiki/ASCII#Control_characters).

## Extended ASCII

ASCII maps each character in a 256 character set to an integer in the interval [0, 255].

Each extended ASCII character is one byte, or 8 bits.

It adds more symbols (e.g., different currency symbols) and accented characters.

```python
>>> [chr(num) for num in range(256)]
['\x00', '\x01', '\x02', '\x03', '\x04', '\x05', '\x06', '\x07', '\x08', '\t', '\n', '\x0b', '\x0c', '\r', '\x0e', '\x0f', '\x10', '\x11', '\x12', '\x13', '\x14', '\x15', '\x16', '\x17', '\x18', '\x19', '\x1a', '\x1b', '\x1c', '\x1d', '\x1e', '\x1f', ' ', '!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ':', ';', '<', '=', '>', '?', '@', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '[', '\\', ']', '^', '_', '`', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '{', '|', '}', '~', '\x7f', '\x80', '\x81', '\x82', '\x83', '\x84', '\x85', '\x86', '\x87', '\x88', '\x89', '\x8a', '\x8b', '\x8c', '\x8d', '\x8e', '\x8f', '\x90', '\x91', '\x92', '\x93', '\x94', '\x95', '\x96', '\x97', '\x98', '\x99', '\x9a', '\x9b', '\x9c', '\x9d', '\x9e', '\x9f', '\xa0', '¡', '¢', '£', '¤', '¥', '¦', '§', '¨', '©', 'ª', '«', '¬', '\xad', '®', '¯', '°', '±', '²', '³', '´', 'µ', '¶', '·', '¸', '¹', 'º', '»', '¼', '½', '¾', '¿', 'À', 'Á', 'Â', 'Ã', 'Ä', 'Å', 'Æ', 'Ç', 'È', 'É', 'Ê', 'Ë', 'Ì', 'Í', 'Î', 'Ï', 'Ð', 'Ñ', 'Ò', 'Ó', 'Ô', 'Õ', 'Ö', '×', 'Ø', 'Ù', 'Ú', 'Û', 'Ü', 'Ý', 'Þ', 'ß', 'à', 'á', 'â', 'ã', 'ä', 'å', 'æ', 'ç', 'è', 'é', 'ê', 'ë', 'ì', 'í', 'î', 'ï', 'ð', 'ñ', 'ò', 'ó', 'ô', 'õ', 'ö', '÷', 'ø', 'ù', 'ú', 'û', 'ü', 'ý', 'þ', 'ÿ']
```

## Unicode

In Python 3, the `str` class is a Unicode string.

Let's call this a string for short.

If we iterate through a string, we iterate a Unicode character at a time.

For example:

```python
>>> [ch for ch in "\u2603\u20A0\u2200"]
['☃', '₠', '∀']
```

`\u` is an escape sequence. Python expects exactly 4 hexadecimal characters to follow (`\x` is an escape sequence for 2 hexadecimal characters and `\U` is an escape sequence for 8 hexadecimal characters).

The string "\u2603\u20A0\u2200" corresponds to the hexadecimal numbers "2603", "20A0", and "2200" and the decimal numbers 9731, 8352 and 8704.

```python
>>> [int("2603", 16), int("20A0", 16), int("2200", 16)]
[9731, 8352, 8704]
```

We can translate these numbers into characters using the `chr` function:

```python
>>> [chr(9731), chr(8352), chr(8704)]
['☃', '₠', '∀']
```

And the characters into numbers using the `ord` function:

```python
>>> [ord('☃'), ord('₠'), ord('∀')]
[9731, 8352, 8704]
```

Unicode is a standard that maps each character in the Unicode character set to a number (called a "code point") in the range [0, 1114111] (called the "codespace"). Only about 100,000 points in the codespace are assigned to character as of 2023.

```python
>>> chr(1114111)
'\U0010ffff'

>>> chr(1114112)
ValueError: chr() arg not in range(0x110000)
```

UTF-8 is an encoding of Unicode code points into bytes.

Let's just look at the first code point in the string. It corresponds to the [Snowman character](http://web.archive.org/web/20230328214106/https://codepoints.net/U+2603?lang=en).

```python
>>> bytes("\u2603", "utf-8")
b'\xe2\x98\x83'
```

If we iterate through a bytes object, we iterate a byte at a time.

```python
>>> [byte for byte in b"\xe2\x98\x83"]
[226, 152, 131]
```

It is stored in binary as: "100000111001100011100010".

```python
>>> bin(131)[2:] + bin(152)[2:] + bin(226)[2:]
'100000111001100011100010'

>>> bin(int.from_bytes(b'\xe2\x98\x83', byteorder=sys.byteorder))[2:]
'100000111001100011100010'
```

How does this relate to the code point of 9731?

UTF-8 is a variable length encoding. It has a number of bytes in the range [1, 4].

The UTF-8 Wikipedia [page](http://web.archive.org/web/20230329002824/https://en.wikipedia.org/wiki/UTF-8) has a "Code point ↔ UTF-8 conversion" table.

Using this table, we can tell that "100000111001100011100010" is a 3 byte encoding:

```
100000111001100011100010
10000011|10011000|11100010
aaxxxxxx|bbyyyyyy|cccczzzz
aaxxxxxx = 10000011 (131)
bbyyyyyy = 10011000 (152)
cccczzzz = 11100010 (226)

xxxxxx = 000011 
yyyyyy = 011000
zzzz = 0010

zzzzyyyyyyxxxxxx
0010011000000011 (9731)
```

In short, UTF-8 adds some binary digits as metadata to facilitate decoding.
 
## Sources

* "Pragmatic Unicode, or, How do I stop the pain?" [video](https://nedbatchelder.com/text/unipain.html)
* http://web.archive.org/web/20230328211242/http://unicode.org/mail-arch/unicode-ml/y2002-m04/0092.html
* https://stackoverflow.com/questions/27331819/whats-the-difference-between-a-character-a-code-point-a-glyph-and-a-grapheme
* https://stackoverflow.com/questions/45010682/how-can-i-convert-bytes-object-to-decimal-or-binary-representation-in-python
* https://stackoverflow.com/questions/44622037/regarding-unicode-characters-and-their-utf8-binary-representation
* https://stackoverflow.com/questions/52539729/encodeutf-8-is-different-from-ord
* https://www.joelonsoftware.com/2003/10/08/the-absolute-minimum-every-software-developer-absolutely-positively-must-know-about-unicode-and-character-sets-no-excuses/