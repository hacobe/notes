# Nand2Tetris

## Boolean Logic

A **gate** is a physical device that implements a boolean function. Gates are typically implemented using **transistors** etched into silicon and packages as **chips**. We use **chip** and **gate** interchangeably, tending to use the latter for simpler instances of the former.

The **Nand** gate implements the following boolean function expressed as a truth table:

|a|b|Nand(a,b)|
|-|-|---------|
|0|0|1|
|0|1|1|
|1|0|1|
|1|1|0|

From the Nand gate, we build the following basic logic gates:

* **Not**: Also known as inverter, this gate outputs the opposite value of its input's value.
* **And**: Returns 1 when both its inputs are 1, and 0 otherwise
* **Or**: Returns 1 when at least one of its inputs is 1, and 0 otherwise
* **Xor**: Also known as exclusive or, this gate returns 1 when exactly one of its inputs is 1, and 0 otherwise
* **Multiplexer**: A multiplexer is a three-input gate.  Two input bits, named `a` and `b`, are interpreted as data bits, and a third input bit, named `sel`, is interpreted as a selection bit. The multiplexer uses `sel` to select and output the value of either `a` or `b`.
* **Demultiplexer**: A demultiplexer performs the opposite function of a multiplexer: it takes a single input value and routes it to one of two possible outputs, according to a selector bit that selects the destination output. The other output is set to 0.

We build **multi-bit** versions of each of these gates. For Not, And, Or and the Xor gates, the input is `n` bits, the operation is applied bitwise and the output is `n` bits. For the multiplexer and demultiplexer, `a` is `n` bits, `b` is `n` bits and `sel` is 1 bit, `sel` determines which of all of `a` or `b` to select and the output is `n` bits.

We build **multi-way** versions of each of these gates. For Not, And, Or and the Xor gates, the input is `n` bits, the operation is applied to each bit in sequence (e.g., `a[0] Or a[1] Or a[2]`) and the output is 1 bit. The `m`-way, `n`-bit multiplexer selects one of its `m` `n`-bit inputs, and outputs it to its `n`-bit output. The selection is specified by a set of `k` selection bits, where $k = \log_2 m$. The `m`-way `n`-bit demultiplexer routes its single `n`-bit input to one of its `m` `n`-bit outputs. The other outputs are set to 0.

## Boolean Arithmetic

From the basic logic gates, we build the following adders:

* **Half-adder**: designed to add two bits
* **Full-adder**: designed to add three bits
* **Adder**: designed to add two n-bit numbers
* **Incrementer**: designed to add 1 to a given number 

The Half-adder takes a 1-bit `a` and a 1-bit `b` as input and returns the `sum`, i.e., the least significant bit of `a + b`, and the `carry`, i.e., the most significant bit of `a + b`, as output.

The Full-adder takes a 1-bit `a`, a 1-bit `b` and a 1-bit `c` as input and returns the `sum`, i.e., the least significant bit of `a + b + c`, and the `carry`, i.e., the most significant bit of `a + b + c`, as output.

The Adder takes an `n`-bit `a` and an `n`-bit `b` as input and returns an `n`-bit output giving the `n` least significant bits of `a + b`. The last carry bit is ignored. If that carry bit is 1, then we have what is known as **overflow**. We decide to ignore overflow only providing the guarantee that the result of adding any two `n`-bit numbers will be correct up to `n` bits.

The Incrementer takes an `n`-bit `x` as input and returns an `n`-bit output giving the `n` least significant bits of `x + 1`. Again, the last carry bit is ignored.

From our adders, we build our **Arithmetic and Logical Unit (ALU)**. The ALU takes an `n`-bit `x`, `n`-bit `y` and `k` control bits, selects an arithmetic or logical function based on the control bits, applies it to `x` and `y` and returns an `n`-bit output. The inputs to the ALU are interpreted as signed integers using two's complement, where the signed integer value is given by $-(b_{n-1} 2^{n-1}) + \sum_{i=0}^{n-2} b_i 2^{i}$ for the binary sequence $b_{n-1} b_{n-2} \ldots b_1 b_0$. As a concrete example, we have an ALU that takes 16 bit inputs, has 6 control bits and computes one of the following functions: 0, 1, -1, `x`, `y`, `Not(x)`, `Not(y)`, `-x`, `-y`, `x + 1`, `y + 1`, `x - 1`, `y - 1`, `x + y`, `x - y`, `y - x`, `x And y`, `x Or y`. It turns out other functions like `x * y` or `x / y` can be reduced to binary addition. We'll have the software stack convert those functions to ones that the ALU can compute.

## Memory

We introduce a **clock** built from a quartz crystal, which emits an electronic signal that oscillates between a low and high state at a constant frequency after a voltage is applied to it. At the start of the tick phase, the clock's signal moves from the high state to the low state. At the end of the tock phase, the signal has moved from the low state to the high state. A **cycle** is the elapsed time between the start of a tick and the end of the subsequent tock.

We use the clock to neutralize noise associated with communication and computation delay in a chip. The clock's cycle length is set just above the maximum delay of any circuit in the chip. We then only react to changes in the chip in cycle transitions. We also use the clock to synchronize computation throughout the chip.

The **data flip flop (DFF)** gate takes a 1-bit data input and a 1-bit clock signal and returns a 1-bit output. The gate changes the value of its output to the value of its data input at the tock of the clock. Otherwise, it ignores the data input. In this way, the gate returns the value of the data input at the last tock of the clock.

It does so using a feedback loop (outputs feeding back into inputs) that locks in (or "latches") the input value at a particular time even after the input value changes. In this way, the gate "remembers" the input value at that particular time. In general, **sequential logic** is logic implemented by circuits that contain feedback loops, while **combinational logic** is logic implemented by circuits that do not contain feedback loops.

From the DFF, we build a 1-bit **register**, which takes a 1-bit data input, a 1-bit load input that enables writes and a 1-bit clock signal and returns a 1-bit output for the state of the register. If the load input is on, then `y(t+1) = x(t)`. Otherwise, the register is latched and `y(t+1) = y(t)`. This 1-bit register is like the DFF except that it has the additional load input. We also build a 16-bit register, which takes a 16-bit data input and a 1-bit load input and returns a 16-bit output.

**Random Access Memory (RAM)** consists of `n` registers. It takes a 16-bit data input, a $k = \log_2(n)$ bit address, a 1-bit load input and a 1-bit clock signal and returns a 16-bit output for the state of the register at the location specified by the address. If the load input is on, then the register at the location specified by the address is set to the value of the data input.

The **Program Counter** is a special register that takes a 16-bit data input, a 1-bit load input, a 1-bit increment input, a 1-bit reset input and a 1-bit clock signal and returns a 16-bit output for the state of the register. If the reset bit is on, then `y(t+1) = 0`. If the load bit is on, then `y(t+1) = x(t)`.  If the increment bit is on, then `y(t+1) = y(t) + 1`. Otherwise, `y(t+1) = y(t)`.

## Computer Architecture

The **von Neumann architecture** consists of memory, a processor and input and output (I/O) devices. The memory is a linear sequence of addressable, fixed-size registers. It stores data and instructions. In storing instructions in memory, the architecture implements the **stored program concept** rather than a programmer having to use a plugboard or a similar mechanism. The processor has an arithmetic and logic unit, a control unit and registers. The control unit fetches an instruction from memory, decodes it and directs the arithmetic and logic unit to execute it. The computer uses **memory mapped I/O**, where the processor can communicate with an I/O device by reading from and writing to a designated area of memory allocated for that device.

## Sources

* Chapters 1-3, 5. The Elements of Computing Systems, 2nd Edition