# Floating point

The bits to represent a floating point number are broken up into:

- sign bit: 0 for positive and 1 for negative
- an 8 bit exponent: "Exponents can be positive or negative, but instead of reserving another sign bit, they're encoded such that 10000000 represents 0, so 00000000 represents -128 and 11111111 represents 127."
- remaining bits for the significand (also called mantissa). Represented like this: $01101 = 0 \cdot 2^{-1} + 1 \cdot 2^{-2} + 1 \cdot 2^{-3} + 0 \cdot 2^{-4} + 1 \cdot 2^{-5}$

The floating point number is called as follows:

sign bit * significand * 2^{exponent}.

## Sources

* https://softwareengineering.stackexchange.com/questions/215065/can-anyone-explain-representation-of-float-in-memory