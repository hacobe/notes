# Synchronous systems

This [article](https://www.sciencedirect.com/topics/engineering/synchronous-system) defines a synchronous system as "one in which transfer of information between combinational blocks is performed in synchrony with a global clock signal." A combinational block is a circuit that only uses combinational logic, i.e., logic where the output is a function of the present input only as opposed to sequential logic, where the logic can depend on the past history of inputs.

Take the example of building an accumulator, i.e., a circuit that executes the following function:

```
int accumulate(int x[N]) {
	int s = 0;
	for (i = 0; i < N; i++) {
		s += x[i];
	}
	return s;
}
```

The naive circuit looks like this:

![accumulator_naive](/img/accumulator_naive.png)

There are 2 problems with it:

1. There is no way to control the iteration of the for loop
2. There is no way to initialize `s` to 0

We fix those problems by adding a register:

![accumulator](/img/accumulator.png)

Then `s` only gets updated at the clock tick.

The combinational logic separated by registers is the basic model for a synchronous system:

![synchronous_system](/img/synchronous_system.png)