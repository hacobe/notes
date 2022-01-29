# Backtracking

From Skeina:

*At each step in the backtracking algorithm, we start from a given partial solution $a = (a_1, a_2, \dots, a_k)$ and try to extend it by adding another element at the end. After extending it, we test whether what we have so far is a complete solution. If not, the critical issue is whether the current partial solution $a$ is potentially extendible to a solution. If so, recur and continue. If not, delete the last element from $a$ and try another possibility for that position if one exists.*

Pseudocode for the backtracking algorithm is as follows: 

	Backtrack(a, k)
		If a is a solution:
			print(a)
		Else:
			k = k + 1
			compute S_k
			while S_k != 0:
				a_k = an element in S_k
				S_k = S_k - a_k
				Backtrack(a, k)

For example, suppose we want to print all permutations of the list [1, 2, 3]. We call Backtrack([], 0). [] is not a solution, so we set k = 1. We compute S_1 = {1, 2, 3}. In the first iteration of the loop, we set a_1 = 1 and S_1 = {2, 3} and call Backtrack([1], 1). In the second iteration, we set a_1 = 2, S_1 = {1, 3} and call Backtrack([2], 1). In the last iteration, we set a_1 = 3, S_1 = {1, 2} and call Backtrack([3], 1). In general, the argument $a$ develops recursively like this [image](https://medium.com/algorithms-and-leetcode/backtracking-e001561b9f28):

![backtracking](/img/backtracking.png)

The backtracking algorithm is actually DFS on a graph where each node represents a partial solution.

## Related problems

* Solving sudoku
* Constructing all subsets of a given set
* Constructing all permutations of a given list
* https://www.geeksforgeeks.org/backtracking-algorithms/
* https://leetcode.com/problems/splitting-a-string-into-descending-consecutive-values/
* https://leetcode.com/problems/binary-watch/

## Sources

* CSE373, 2016
	* [Lecture 16 - Backtracking I](https://www.youtube.com/watch?v=_ieNMJuTr4U) (33 to 49 min)	