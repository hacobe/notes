# Flip-flops

Consider an OR gate that takes inputs $A$ and $B$ and returns a high signal if $A$ has a high signal or $B$ has a high signal (or both have a high signal) and returns a low signal otherwise. Add a wire that also feeds the output back into one of the inputs (say the input $B$) instead of that input being determined by an external source.

![or_gate_with_feedback](/img/or_gate_with_feedback.png)

This **OR gate with feedback** starts with $A$ and $B$ having a low signal. If we have a low signal flowing through $A$, then the OR gate outputs a low signal, that low signal feeds back into $B$ and the OR gate continues to output a low signal. If we send a high signal through $A$, then the OR gate outputs a high signal, that high signal feeds back into $B$ and the OR gate continues to output a high signal. If we then send a low signal through $A$, the OR gate continues to output a high signal (because of the high signal feeding back into $B$), that high signal continues to feeds back into $B$ and the OR gate continues to output a high signal. In this way, the OR gate outputs a high signal irrespective of the signal flowing into $A$ after the first time sending a high signal through $A$.

We now modify the gate to enable us to change the output of the gate after the first time sending a high signal through an input.

Consider the **SR latch**:

![sr_latch](/img/sr_latch.png)

It has a Reset input ($R$), a Set input ($S$), an output ($Q$) and the complement of that output ($\bar{Q}$). The SR latch starts with $R$ and $S$ having a low signal. If both inputs to a NOR gate have a low signal, then a NOR gate will output a high signal. Otherwise, a NOR gate will output a low signal. The SR latch starts with all the inputs having low signal suggesting that both of the NOR gates will output a high signal. However, one of the NOR gates will starting outputting a high signal a little bit before the other NOR gate. Suppose the top NOR gate starts outputting a high signal first. In this case, that high signal is fed back into the bottom NOR gate, that bottom NOR gate outputs a low signal, that low signal is fed back into the top NOR gate and that top NOR gate continues to output a high signal. In this way, the top NOR gate outputs a high signal ($Q$) at the start and the bottom NOR outputs a low signal ($\bar{Q}$) at the start. 

![sr_latch_top](/img/sr_latch_top.png)

If the bottom NOR gate had started outputting a high signal before the top NOR gate, then the bottom NOR gate would output a high signal ($\bar{Q}$) at the start and the top NOR gate would output a low signal ($Q$) at the start.

![sr_latch_bottom](/img/sr_latch_bottom.png)

Suppose that the top NOR gate is outputting a high signal and the bottom NOR is outputting a low signal. If we send a high signal through $R$, then the top NOR gate starts outputting a low signal, that low signal feeds back into the bottom NOR gate, the bottom NOR starts outputting a high signal, that high signal feeds back into the top NOR gate and the top NOR gate continues to output a low signal. In this way, the top NOR gate outputs a low signal ($Q$) and the bottom NOR gate outputs a high signal ($\bar{Q}$) after sending a high signal through $R$.

Suppose instead that the top NOR gate is outputting a low signal and the bottom NOR is outputting a high signal. If we send a high signal through $R$, then the top NOR gate continues to output a low signal and we have the same behavior as before: the top NOR gate outputs a low signal ($Q$) and the bottom NOR gate outputs a high signal ($\bar{Q}$) after sending a high signal through $R$.

Suppose that the top NOR gate is outputting a high signal and the bottom NOR is outputting a low signal. If we send a high signal through $S$, then the bottom NOR gate continues to output a low signal, the top NOR gate continues to output a high signal ($Q$) and the bottom NOR gate continues to output a low signal ($Q$).

Suppose instead that the top NOR gate is outputting a low signal and the bottom NOR is outputting a high signal. If we send a high signal through $S$, then the bottom NOR gate starts outputting a low signal, that low signal feeds back into the top NOR gate, the top NOR gate starts outputting a high signal, that high signal feeds back into the bottom NOR gate and the bottom NOR gate continues to output a low signal. In this way, the top NOR gate outputs a high signal ($Q$) and the bottom NOR gate outputs a low signal ($\bar{Q}$) after sending a high signal through $S$.

In general, if we send a high signal through $R$, then the SR latch will continue to output a low signal ($Q$) irrespective of the signal flowing into $R$ after as long as the low signal into $S$ continues. If we send a high signal through $S$, then the SR latch will continue to output a high signal ($Q$) irrespective of the signal flowing through $S$ after as long as the low signal into $R$ continues. We consider the case of a high signal flowing through both $R$ and $S$ to be invalid.

The SR latch acts like a light switch. The light switch starts out either flipped up or flipped down. If it starts flipped up, then the light is on and stays on until you flip it down (it "remembers" its last state). While the light switch is flipped up, pushing up again on the light switch does not have any effect. If you push down on the light switch, then the light turns off and stays off until you flip it up (again "remembering" its last state). While the light switch is flipped down, pushing down again on the light switch does not have any effect. Whether the light switch starts flipped up or flipped down does not change this dynamic. Pushing the light switch up and down at the same time does not make sense.

The SR latch takes 2 gates and feeds the output of each into the input of the other. When 1 gate outputs a high signal, it forces the other gate to output a low signal, which keeps the first gate outputting a high signal and so on. The SR latch has 2 states depending on which one of the 2 gates is outputting the high signal. The feedback loop locks the SR latch in its last state. The $S$ input overpowers the feedback loop to have the gate connected to it output the high signal. The $R$ input overpowers the feedback loop to have the gate connected to it output the high signal.

The **D latch** is like an SR latch, but instead of having a Set input and a Reset input, it has one input ($D$) where a low signal for that input gives the Set operation and a high signal for that input gives the Reset operation. It also has an Enable input ($EN$). The output only changes when the Enable input has a high signal.

![d_latch](/img/d_latch.png)

The **D flip-flop** adds a small circuit before the Enable input of the D latch that takes as input a Clock and outputs a pulse on the rising edge of the clock's waveform.

![d_flip_flop](/img/d_flip_flop.png)

This frame shows the waveforms of the Clock, Enable, D and Q for the D flip-flop ($\bar{Q}$ is ignored):

![d_flip_flop_waveforms](/img/d_flip_flop_waveforms.png)

The D flip-flop stores the input value until the next clock tick. It ignore changes in between the clock ticks.

## Sources

* Ben Eater
	* [SR latch](https://www.youtube.com/watch?v=KM0DdEaY5sY)
	* [D latch](https://www.youtube.com/watch?v=peCh_859q7Q)
	* [D flip](https://www.youtube.com/watch?v=YW-_GkUguMM)