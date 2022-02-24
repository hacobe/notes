# Correctness proof

Consider the algorithm:

		def multiply(m, a):
			r = 0
			i = 0
			while i < m:
				r = r + a
				i = i + 1
			return r

Prove that this algorithm returns m * a.

1) Find a loop invariant (LI): r = i * a

2) Base case: prove that LI is true before the loop.

		r = 0 (base condition: r = 0)
		  = 0 * a
		  = i * a (base condition: i = 0)

3) Induction step: assume that LI is true at the start of each iteration and prove that holds at the end of each iteration

		r_{t+1} = r_t + a_t = (i_t * a_t) + a_t = (i_t + 1) * a_t = i_{t+1} * a_{t+1}

4) Prove that loop terminates

		m stays the same, while i increases by 1 at each step

5) Prove correctness: the loop terminates when i = m

## Source

* How to Solve It By Computer
* https://www.youtube.com/watch?v=GSvqF48TVM4