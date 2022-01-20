# Two's complement

In a previous post on binary addition, we constructed a simple calculator using buckets, tubes and water. We can use this calculator to add any two positive numbers where the sum doesn't exceed the maximum number we can store in the output. And we showed how this model predicts certain errors when adding unsigned 8 bit numbers in Python in the post on overflow.

What if you want to subtract numbers?

It turns out we can make use of our previous calculator if we represent negative numbers in binary using a representation called "2's complement". In 2's complement, the leftmost, most significant bit in an $n$-bit binary number is worth $-2^{n-1}$ instead of $2^{n-1}$ and all the other bits are worth the same as in the normal binary representation. For example, 1000 in 2's complement is equal to $-2^3 = -8$ and 1100 is equal to $-2^3 + 2^2 = -4$.

Here's a quick way to find the 2's complement representation of a negative number:

1. Find the binary representation of the absolute value of the negative number you want to represent
2. Flip each digit in the binary representation
3. Add 1

Suppose we have 2 buckets, i.e. 2 bits, to represent the output in our calculator. If we add only positive numbers, then we have:

	00 (0)
	01 (1)
	10 (2)
	11 (3)

If we want to add positive and negative numbers, then we have:

	00 (0)
	01 (1)
	10 (-2)
	11 (-1)

The "E" bucket (error / overflow bit) we had in the case of adding positive numbers no longer has the same meaning when we add signed numbers.

The error bucket is the last carry out bucket. For positive numbers, it signals an overflow:

	 11  (carry)
	  11 (3)
	 +01 (1)
	 ---
	  00 (0)

In the case above, the error bit is on and rightly so, because the sum is telling us that 3 + 1 = 0.

But if we're using signed numbers, the same addition is valid:

	 11  (carry)
	  11 (-1)
	 +01 (1)
	 ---
	  00 (0)

Still, we can have errors when adding signed numbers:

	10  (carry)
	 10 (-2)
	+11 (-1)
	--- 
	 01 (1)

The calculation above is telling us that -2 + (-1) = 1. For signed numbers, an error is detected if the last carry in does not equal the last carry out, i.e., if the XOR of the last two carry bits is true. The last two bits in the carry in the example above are 1 and 0, which are different, so we know there's an error. In the example before that, the last two bits in the carry are 1 and 1, which are the same, so we're good.

As with unsigned integer overflow, we can see the weird mistakes in Python:

	import numpy as np

	x = np.array([2**7 - 1, 2**7-1], dtype='int8')

	x
	array([127, 127], dtype=int8)

	np.sum(x, dtype='int8')
	-2

We see how we would get this answer:

	01111111  (carry)
	 01111111 (127)
	+01111111 (127)
	---------
	 11111110

11111110 = $-2^7 + 2^6 + 2^5 + 2^4 + 2^3 + 2^2 + 2^1$ = -2