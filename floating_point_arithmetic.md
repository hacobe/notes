# Floating-point arithmetic

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

The IEEE 754 standard also defines other floating point formats with varying numbers of bits and levels of precision (e.g., 64 bits for double precision).

A fundamental difficulty is the rounding error introduced when we store real numbers on a computer with a finite number of bits. The rounding error is especially problematic when it compounds across many operations.

There are 2 types of rounding error:

1. Overflow: A number with large magnitude is approximated as negative or positive infinity.
2. Underflow: A number near 0 is rounded down to 0.

Overflow is a problem, because it can result in not-a-number  (NaN) values. What happens is that numbers overflow, get approximated as negative or positive infinity and then get used in arithmetic operations that result in NaNs.

Underflow is a problem, because:

* It can result in a divide by 0 exception being thrown (In Python, 1/0 results in a ZeroDivisionError)
* It gets used in an operation that result in negative or positive infinity, e.g., log(0), which then runs into the same problems we saw with overflow.

## Sources

* [Single-precision floating-point format - Wikipedia](https://en.wikipedia.org/wiki/Single-precision_floating-point_format)
* Goodfellow, Deep learning, Section 4.1
