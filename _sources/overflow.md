# Overflow

When we type two numbers into a calculator and ask for the sum, we don't think too hard about how the calculator arrives at the answer. Implicitly, we might have a mental model of the calculator as doing what we do when we add 2 numbers, but much faster and more carefully. That's not a very good model. In particular, that model doesn't predict the errors we get with calculators in certain scenarios.

A better model is the one described in my post on binary addition. The practical takeaway of the model is that a computer represents numbers in binary with some fixed, finite number of digits. We can also use the model to predict the errors we get when the sum that we've asked for exceeds the limit.

For example, suppose the computer we have only stores numbers that can be represented with 8 binary digits, i.e. we have 16 input tubes in our fluidic computer.

The maximum number we can store is 11111111, which is $\sum_{i=1}^8 2^{i-1} = 2^7 = 255$. What happens when we add 255 to 255?

	carry 11111111
	       11111111
	      +11111111
	      ----------
	      111111110

We can't store the last 1 in the answer (it's the $C_{out}$ bucket in our fluidic computer), so it leaves us with 11111110, or 254.

We can observe this behavior in Python:

	import numpy as np

	x = np.array([2**8 - 1, 2**8-1], dtype='uint8')

	x
	array([255, 255], dtype=uint8)

	np.sum(x, dtype='uint8')
	254

There's some [nuance](https://web.archive.org/web/20180901001354/http://mortada.net/can-integer-operations-overflow-in-python.html) to this, but most of the time we don't notice it, because the dtype for an integer numpy array is int64. 