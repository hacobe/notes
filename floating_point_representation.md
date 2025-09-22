# Floating-point representation

Computers perform arithmetic operations on numbers encoded as sequences of bits.

For example, an Arithmetic Logic Unit (ALU) is a circuit that takes 2 $n$-bit inputs, performs some arithmetic or logical operation on those inputs (e.g., addition, subtraction, multiplication, division, bitwise negation, etc) and returns an $n$-bit output. We interpret each input or output with bits $x_0, x_1, \ldots, x_{n-1}$ as the unsigned integer $\sum_{i=0}^{n-1} x_i 2^i$ or as the signed integer $-x_{n-1} 2^{n-1} + \sum_{i=0}^{n-2} x_i 2^i$ using Two's complement.

A Floating-Point Unit (FPU) is a circuit that takes floating-point inputs encoded according to a standard format, performs arithmetic operations on those inputs (e.g., floating-point addition, subtraction, multiplication, division, square root, etc), and returns a floating-point output.

The IEEE 754 standard defines a format for the binary representation of floating-point numbers.

The single precision (i.e., 32 bit) floating-point number in the standard decomposes as follows:

* sign $s$ (1 bit)
* exponent $x_7 x_6 \dots x_0$ (8 bits), where $x = \sum_{i=0}^7 x_i 2^i$ 
* fraction $f_{22} f_{21} \dots f_0$ (23 bits), where $f = \sum_{i=0}^{22} f_i 2^i$

The value is computed as $(-1)^s \times 2^{x - 127} \times \left(1 + \sum_{i=0}^{22} f_{22-i} 2^{-i-1} \right)$ except if $x = 0$ or $x = 255$. If $x = 0$ or $x = 255$, then the value is determined according to the following table:

|s|x|f|value|
|-|-|-|-----|
|0|255|=0|Infinity|
|1|255|=0|-Infinity|
|0|255|!=0|NaN|
|1|255|!=0|NaN|
|0|0|=0|0|
|1|0|=0|-0|
|0|0|!=0|$2^{-126} \times \sum_{i=0}^{22} f_{22-i} 2^{-i-1}$|
|1|0|!=0|$-2^{-126} \times \sum_{i=0}^{22} f_{22-i} 2^{-i-1}$|

The IEEE 754 standard also defines other floating point formats with varying numbers of byte and levels of precision (e.g., 8 bytes for double precision).

## Sources

* [Single-precision floating-point format - Wikipedia](https://en.wikipedia.org/wiki/Single-precision_floating-point_format)
