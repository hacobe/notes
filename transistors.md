# Transistors

Consider a set of dominoes arranged in a line with a domino in the middle of the line on a sliding track. We place a bell at the end of the line. To start this contraption, we tip the domino at the head of the line. If the middle domino is in its place, then all the dominoes fall including the last one, which rings the bell. Otherwise, the first half of the line falls, but not the second half, because of the gap in the middle of the line, and the bell does not ring.

Now replace the dominoes, sliding track, and bell with electrical components. Instead of tipping the domino at the head of the line, we apply voltage from a power source. Instead of a cascade of falling dominoes, we have the flow of electrical current through a wire. Instead of the bell, we have a light bulb at the end of the circuit. Instead of the middle domino on a sliding track, we have a gate that can open or close the circuit. If the gate is closed, current flows from the power source through the complete circuit and the light bulb turns on. If the gate is open, the circuit is broken, current cannot flow, and the light bulb remains off. We have constructed a switch.

A **switch** is an electrical component with a gate that, when closed, allows current to flow through the circuit and, when open, blocks current from flowing through the circuit.

![A switch.](img/switches.png){width=50%}

A **transistor** is a switch whose gate can be opened or closed by an electrical signal rather than mechanical action.

We can compose transistors to build a **logic gate**, i.e., a physical device that implements a boolean functions.

For example, we can arrange 2 transistors in series to build an AND gate, which takes 2 boolean inputs and returns true if both inputs are true and false otherwise. Or we can arrange 2 transistors on parallel tracks to build an OR gate, which takes 2 boolean inputs and returns true if either input is true or both inputs are true and false otherwise.

![An AND gate and an OR gate built from switches.](img/and_or_gates.png){width=50%}

We can further compose gates to build circuits that perform complex arithmetic and logical computations.

From the 1970s to 2010s, the number of transistors in a computer has doubled every 2 years (Moore's Law is the observation of this trend). As of 2025, a computer uses billions of transistors (e.g., the [Apple M3 Ultra](https://en.wikipedia.org/wiki/Apple_M3) computer chip has 184 billion transistors).

## Additional topics

* How to build a NOT gate from transistors

## Sources

* [Lecture 9 - UC Berkeley, CS61C, Spring 2015](https://www.youtube.com/watch?v=zpGzXfWRk70&list=PLhMnuBfGeCDM8pXLpqib90mDFJI-e1lpk&index=9))