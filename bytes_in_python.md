# Bytes in Python

Binary data in Python has type `bytes`.

We can construct binary data by prefixing a string with `b`.

For example:

```python
assert isinstance(b"a", bytes)
```

Each character of the string is interpreted as an ASCII character.

We can convert the binary data to an 8-bit integer:

```python
assert int.from_bytes(b"a", byteorder="big", signed=True) == 97
```

And we can convert the integer back into binary data:

```python
assert (97).to_bytes(length=1, byteorder="big", signed=True) == b"a"
```

We can also construct binary data by using hexadecimal characters prefixed by `\x` instead of ASCII characters:

```python
assert isinstance(b"\x05", bytes)
```

We convert the binary data to an integer:

```python
assert int.from_bytes(b"\x05", byteorder="big", signed=True) == 5
```

And can convert the integer back to binary data:

```python
assert (5).to_bytes(length=2, byteorder="big", signed=True) == b"\x00\x05"
```

If we try to treat a negative integer as unsigned, we get an error:

```python
import pytest
with pytest.raises(OverflowError):
	(-5).to_bytes(length=2, byteorder="big", signed=False)
```

When we index into binary data, we get an unsigned 8-bit integer, not binary data:

```python
assert (b"hello")[0] == 104
assert [i for i in b"hello"] == [104, 101, 108, 108, 111]
```

When we slice into binary data, we get binary data:

```python
assert (b"hello")[0:1] == b"h"
```

We can convert an integer to a binary string (for the mathematical representation rather than the storage representation):

```python
assert bin(5) == "0b101"
assert bin(-5) == "-0b101"
```

And a binary string back to an integer:

```python
assert int("0b101", 2) == 5
assert int("-0b101", 2) == -5
```

Similarly, we can convert an integer to a hexadecimal string:

```python
assert hex(5) == "0x5"
assert hex(-5) == "-0x5"
```

And a hexadecimal string back to an integer:

```python
assert int("0x5", 16) == 5
assert int("-0x5", 16) == -5
```

Note that `int` interprets the string (without the negative sign) as an unsigned integer.