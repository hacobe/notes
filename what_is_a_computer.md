# What is a computer?

A computer is like a [Rube Goldberg machine](https://en.wikipedia.org/wiki/Rube_Goldberg_machine): a contraption that performs a task through an elaborate chain reaction of physical events. It starts off with a domino falling over, a marble rolling down a ramp or a lever being pulled. It ends with the ringing of a bell, the lighting of a candle or the dispensing of toothpaste. In the case of a computer, we set up the contraption so as to provide the answer to a logical question.

![A Rube Goldberg machine](img/rube_goldberg.png)

For example, we can design a contraption to determine whether or not we need an umbrella based on whether or not it's raining or overcast. To do so, we arrange a set of dominoes like this:

![Dominoes arranged in the shape of an upside down Y](img/domino_or_gate.jpg)

If it's raining, we tip over the domino on the bottom left. If it's overcast, we tip over the domino on the bottom right. If it's raining or overcast or it's raining and it's overcast, then all the dominoes eventually fall. Otherwise, none of the dominoes fall. If the last domino falls, we need an umbrella.

This contraption is an example of an OR gate. An OR gate is a physical device that takes 2 or more binary inputs and outputs true if any of its inputs are true and outputs false otherwise. In this case, the OR gate takes 2 binary inputs. The first input is whether or not it's raining. The second input is whether or not it's overcast. The output is whether or not we need an umbrella.

An OR gate is an example of a logic gate. A logic gate is a physical device that implements a function that takes one or more binary inputs and returns a single binary output. Other examples of logic gates include an AND gate, a NOT gate and a NAND gate. An AND gate takes 2 or more binary inputs and returns true if all of its inputs are true and returns false otherwise. A NOT gate takes a single binary input and returns true if that input is false and returns false if that input is true. A NAND gate takes 2 or more binary inputs and returns the same output as if we fed its input through an AND gate followed by a NOT gate.

By composing a large number of these logic gates, we can answer complex logical questions. For example, here is a calculator built from over 10,000 dominoes that can determine the sum of 2 small numbers (and a [video](https://www.youtube.com/watch?v=OpLU__bhu2w) of that calculator in action):

![A domino calculator](img/domino_calculator.jpg)

In fact, it turns out that we can build a general-purpose computer entirely out of NAND gates (the [Nand to Tetris](https://www.nand2tetris.org) course walks through how to do this).
