# Computer chip

A computer chip is any kind of [integrated circuit](https://en.wikipedia.org/wiki/Integrated_circuit). A chip can contain multiple processors. A processor can contain multiple cores. A core can contain multiple hardware threads. A hardware thread consists of a set of registers and a program counter, which stores the information needed to resume executing a sequence of instructions after it has been paused. Multiple hardware threads improve the utilization of a core by switching threads when one is idle (e.g., waiting on data to be retrieved from memory, because of a cache miss).[^1] The number of hardware threads that a chip can run is the number of cores multiplied by the number of hardware threads. If you run `/usr/sbin/sysctl -a | grep hw`, then the number of cores is given by the `physicalcpu` field and the total number of hardware threads on the chip is given by the `logicalcpu` field. The operating system “multiplexes” software threads across the available hardware threads.

## Sources

* UC Berkeley, CS61C, Spring 2015
	* [Lecture 19](https://www.youtube.com/watch?v=2jltTEyiffc&list=PLhMnuBfGeCDM8pXLpqib90mDFJI-e1lpk&index=20), CS61C
* https://stackoverflow.com/questions/19225859/difference-between-core-and-processor

[^1]: With hyperthreading, a core can also contain multiple virtual cores, so that multiple hardware threads can be executed simultaneously, but I don’t discuss hyperthreading here.