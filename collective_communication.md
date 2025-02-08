# Collective communication

We assume a simple model for the time it takes to communicate a message:

```
t_s + m * t_w
```

where:

* t_s is the latency in seconds, i.e., the fixed cost of sending a message
* m is the number of bytes in the message
* t_w is the inverse throughput in seconds per byte, i.e., the variable cost per byte of sending a message

Note that this model assumes that the time to send a message between two nodes is independent of their relative location in the network. For example, the time to communicate between node 0 and node 1 is the same as communicating between node 0 and node 7 even though node 0 and node 1 might be directly connected and node 0 and node 8 may require traversing through multiple links. A more complex model would include how many links must be traversed to get from one node to another, which depends on the network topology. Still, the simple model is reasonably accurate for modern parallel computers (Introduction to Parallel Computing, Chapter 4).

One exception to the accuracy of the model occurs when there is congestion. The effect of congestion is to scale up t_w (or equivalently scale down the throughput). It's hard to estimate the scaling factor precisely, but a lower bound is p/b, where p is the number of processes and b is the bisection width of the network giving us:

```
t_s + m * t_w * (p/b)
```

The bisection width is the minimum number of links needed to divide the network into 2 equal partitions. It identifies the bottleneck in a network. The lower bound is from the worst-case scenario of every process sending a message and those messages have to flow through the bottleneck represented by the bisection.

Usually, we do not explicitly calculate the scaling factor, but make a note of algorithms that may result in congestion.

## Sources

* Introduction to Parallel Computing
* https://en.wikipedia.org/wiki/Collective_operation
* https://en.wikipedia.org/wiki/Broadcast_(parallel_pattern)