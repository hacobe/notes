# Binary addition

We can build circuit to perform arithmetic using logic gates.

We start by building a circuit to add 2 bits $A$ and $B$.

Here are all the possibilities:

|A|B|A+B|
|-|-|---|
|0|0|00|
|1|0|01|
|0|1|01|
|1|1|10|

The $A+B$ columns shows the value of $A+B$ in binary, where an $n$-bit binary number with binary digits $b_{n-1} \ldots b_1 b_0$ has the value $\sum_{i=0}^{n-1} b_i 2^i$.

The **half adder** is a circuit that takes as input 2 bits $A$ and $B$ and outputs a sum bit $S$ and a carry bit $C$:

|A|B|S|C|
|-|-|-|-|
|0|0|0|0|
|0|1|1|0|
|1|0|1|0|
|1|1|0|1|

$S$ is the least significant bit of the sum and $C$ is the most significant bit of the sum. Alternatively, we can think of $S$ as $A+B$ correct up to 1 digit and $C$ as the overflow into the next digit of a multi-digit addition.

We implement the half adder by sending $A$ and $B$ through an XOR gate, i.e., an exclusive or gate, to get $S$ and through an AND gate to get $C$. The XOR gate takes as input 2 bits and returns true if exactly 1 input is true and false otherwise.

The **full adder** is a circuit that takes 3 bits ($A$ and $B$ and a carry bit $C_{in}$) and returns a sum bit $S$ and a carry bit $C_{out}$:

|A|B|Cin|S|Cout|
|-|-|---|-|----|
|0|0|0|0|0|
|0|0|1|1|0|
|0|1|0|1|0|
|0|1|1|0|1|
|1|0|0|1|0|
|1|0|1|0|1|
|1|1|0|0|1|
|1|1|1|1|1|

We build an adder that takes multiple bits by composing full adders. For example, here is an adder that takes as input 2 4-bit binary numbers and returns a 4-bit sum and a 1-bit carry, where the sum is correct up to 4 bits.

![A 4-bit ripple carry adder.](img/4_bit_ripple_carry_adder.png){width=50%}

We implement the full adder from 2 half adders. The first half adder takes $A$ and $B$ as inputs and outputs $S_0$ and $C_0$. The second half adder takes $S_0$ and $C_{in}$ as inputs and outputs $S$ and $C_1$. We then feed $C_0$ and $C_1$ through an OR gate to get $C_{out}$.

## Sources

* [Adder (electronics) - Wikipedia](https://en.wikipedia.org/wiki/Adder_(electronics))