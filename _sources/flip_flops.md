# Flip-flops

A flip-flop, or a latch, is a circuit that can store a bit of information. An n-bit register is comprised of n flip-flops.

![flip_flops](/img/flip_flops.png)

Each individual flip-flop on the right looks like the register on the left. It has a data input D, a data output Q and a clock input CLK.

The flip-flop is an example of a sequential logic circuit, which is defined by the output depending "not only on the present value of its input signals but on the sequence of past inputs, the input history as well" (https://en.wikipedia.org/wiki/Sequential_logic).

Ben Eater does a great job of explaining how a D-type flip-flop works (see the "Sources" section). My exposition is based heavily on his.

Start with an OR gate, but add a wire that feeds the output of the gate back into one of the two inputs of the gate.

![or_gate_with_feedback](/img/or_gate_with_feedback.png)

Call the value of the two inputs $a_t$ and $b_t$ at time $t$ and call the output $c_t$. With $a_t$ defined by an external user of the circuit, the following equations describe the logic of the circuit:

$b_0 = 0$

$b_t = c_{t-1}$ for $t \gt 0$

$c_t = a_t + b_t$ (the + denotes the OR operation)

Suppose we have $a_0 = 0, a_1 = 0, a_2 = 0, a_3 = 1, a_4 = 0, a_5 = 0, a_6 = 1, \dots$. $c_t = 0$ for $t \le 2$ and $c_t = 1$ for $t \ge 3$. In others, the output of the circuit is 0 until the user controlled input is set to 1 and then the output of the circuit is 1 for all time steps after that. The circuit "latches" on to that first 1 and never lets go.

It'd be nice if we could change the output of the circuit after the first 1. The SR latch circuit accomplishes that. Here's the circuit:

![sr_latch](/img/sr_latch.png)

It has a Set input ($S$), a Reset input ($R$), an output ($Q$) and the complement of that output ($\bar{Q}$). If $S$ is set to 1, then the output $Q$ holds 1 no matter the value of $S$ afterwards as long as $R$ is not set. If $R$ is set to 1, then the output $Q$ holds 0 no matter the value of $R$ afterwards as long as $S$ is not set. Setting both $S$ and $R$ at the same time is considered invalid input.

The D latch is like an SR latch, but instead of having a Set input and a Reset input, it has one input ($D$) where a 0 for that input gives the Set operation and a 1 for that input gives the Reset operation. It also has an Enable input ($EN$). The output only changes when the Enable input is set.

![d_latch](/img/d_latch.png)

The D flip-flop adds a small circuit before the Enable input that takes as input a Clock and outputs a pulse on the rising edge of the clock's waveform.

![d_flip_flop](/img/d_flip_flop.png)

Ben draws the waveforms of the Clock, Enable, D and Q for the D flip-flop in this frame ($\bar{Q}$ is ignored):

![d_flip_flop_waveforms](/img/d_flip_flop_waveforms.png)

The flip-flop stores the input value until the next clock tick. It ignore changes in between the clock ticks.

## Sources

* Ben Eater
	* [SR latch](https://www.youtube.com/watch?v=KM0DdEaY5sY)
	* [D latch](https://www.youtube.com/watch?v=peCh_859q7Q)
	* [D flip](https://www.youtube.com/watch?v=YW-_GkUguMM)
* UC Berkeley, CS61C, Spring 2015
	* [Lecture 9](https://www.youtube.com/watch?v=zpGzXfWRk70&list=PLhMnuBfGeCDM8pXLpqib90mDFJI-e1lpk&index=9)
	* [Lecture 10](https://www.youtube.com/watch?v=GCWcJ-Ng9EA&list=PLhMnuBfGeCDM8pXLpqib90mDFJI-e1lpk&index=10)