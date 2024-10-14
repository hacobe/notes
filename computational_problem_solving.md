# Computational problem solving

A short guide to computational problem solving inspired by Polya's How to Solve It.

## Orientation

We start by discussing a specific orientation towards problem solving. Specifically, that **problem solving should not feel too difficult**. In fact, we should take the feeling of confusion or frustration in the course of problem solving as a sign for us to take a step back and simplify the problem. We imagine tackling a problem as climbing a mountain face. An experienced climber moves with grace and economy. They only very rarely exert themselves to leap towards the next hold. Similarly, we take small, concrete and carefully chosen steps. We try to do what seems obvious. And we build up our understanding of the problem incrementally.

## Four phases

Some quick notes on Polya's four phases of problem solving for computational problems.

### Understand the problem

* Restate the problem in your own words
* Define the interface with typed inputs and outputs and their characteristics (e.g. whether the input is sorted)
* Get the answer by hand for a "right-sized" example. Pick an example that's not too simple that it misses aspects of the problems, but not too complex you bogged down in it. Also, don't pick an edge case yet. It should test understanding and be useful for debugging later.
* After working through the initial example, think of edge cases
* Ask questions

### Devise a plan

* Sketch out the interface at each layer
* Define important types
* Test the design by using lower layer functions without implementing them

### Carry out the plan

* If the implementation is hard, go back to a previous phase

### Look back

* Explain the solution and the key insights clearly

## Short Dictionary of Heuristics

### Recurrence relation

https://leetcode.com/problems/count-the-number-of-winning-sequences

We can think of the solution to the problem as an evaluation of the function `f(m)` that returns the number of winning sequences for Bob if he's not allowed to repeat the same move in two consecutive rounds and with Alice's moves are given by `s[:m]`. In particular, we need to return `f(n)`, where `n == len(s)`.

We might be tempted to try to define `f(m)` in terms of `f(m-1)`. However, in order to build on the previous solutions, we need to know (1) the score at the end of the previous round and (2) Bob's last move. Therefore, we define the function `g(m,i,j)` that returns the number of sequences (winning or otherwise) that Bob has if he's not allowed to repeat the same move in two consecutive rounds and the score at the end is `i` with Alice's move given by `s[:m]` and Bob's last move given by `j`. We also define the function `h(a,b)`, which returns 1 if Bob wins the round by playing `b` when Alice `a`, -1 if Bob loses with those moves and 0 if Alice and Bob tie. We can then define a recurrence relation for `g`: $g(m,i+h(s[m-1],j),j) = sum_{i=-n}^n sum_{j' \neq j} g(m-1,i,j')$. We then get `f(m)` by taking `f(m) = \sum_{i=1}^n sum_j g(m,i,j)`, i.e., summing up the sequence counts for all the sequences that end in a positive score.

```python
def fun(s):
	n = len(s)
	s = ["EFW".find(s[i]) for i in range(len(s))]

	# fn[m, i, j] = the number of valid sequences that Bob has if Alice's moves
	# are given by s[:m] and that result in a score of n-i and where Bob's last
	# move was j.
	fn = [[[0 for _ in range(3)] for _ in range((2*n)+2)] for _ in range(n+1)]

	# moves_to_score[r,c] = the score in a round if Alice plays r and Bob plays c.
	moves_to_score = [
		[0, 1, -1],
		[-1, 0, 1],
		[1, -1, 0]
	]

	for j in range(3):
		i = moves_to_score[s[0]][j]
		fn[1][n+i][j] = 1

	for m in range(2, n+1):
		for i in range((2*(n-1))+2):
			for j in range(3):
				p = moves_to_score[s[m-1]][j]
				for jp in range(3):
					if j == jp:
						continue
					fn[m][i+p][j] += fn[m-1][i][jp]

	ans = 0
	for i in range(n+1, (2*n)+2):
		for j in range(3):
			ans += fn[n][i][j]

	# The problem asks us to mod the answer.
	return ans % (10**9 + 7)
```

### Look for a pattern

https://leetcode.com/problems/construct-the-minimum-bitwise-array-ii

We notice that `ans[i] | (ans[i] + 1)` must always be greater than `ans[i]`. If `ans[i] | (ans[i] + 1) == nums[i]`, then `ans[i]` must be less than `nums[i]`. We can use this observation to construct a brute force solution:

```python
def get_min_value(num):
	for cand in range(num):
		if cand | (cand + 1) == num:
			return cand
	return -1

def fun(nums):
	ans = []
	for num in nums:
	    ans.append(get_min_value(num))
	return ans
```

How can we improve on it?

Let's look for a pattern.

```python
def get_min_value(num):
	for cand in range(num):
		if cand | (cand + 1) == num:
			return cand
	return -1

for num in range(2, 11):
	a = get_min_value(num)
	print(num, a)
```

Here's the output of this program:

```
2 -1
3 1
4 -1
5 4
6 -1
7 3
8 -1
9 8
10 -1
```

We immediately notice that `get_min_value` returns -1 for every even number. If a number `x` is even, then the least significant bit of its binary representation is 0. The least significant bit of `x+1` must then be 1. The least significant bit of `x | (x + 1)` must then also be 1. But then `x | (x + 1)` cannot equal `x`, because the least significant bit of `x` is 0.

Let's revise our program to look for a pattern in odd numbers:

```python
def get_min_value(num):
	for cand in range(num):
		if cand | (cand + 1) == num:
			return cand
	return -1

for num in range(3, 30, 2):
	a = get_min_value(num)
	print(num, a)
```

Here's the output of this program:

```
3 1
5 4
7 3
9 8
11 9
13 12
15 7
17 16
19 17
21 20
23 19
25 24
27 25
29 28
```

We notice that `num - a` is a power of 2. We rewrite our original program to only check `a` such that `num - a` is a power of 2 making the time complexity `O(nlog(m))` instead of `O(nm)`, where `n` is the `len(nums)` and `m` is the `max(nums)`.

```python
def get_min_value(num):
	if num % 2 == 0:
		return -1
	a = -1
	diff = 1
	while diff <= num:
		# diff = num - cand
		cand = num - diff
		if cand | (cand + 1) == num:
			a = cand
		diff *= 2
	return a

def fun(nums):
	ans = []
	for num in nums:
	    ans.append(get_min_value(num))
	return ans
```
