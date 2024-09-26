# Sliding window

Pseudocode for the sliding window algorithm:

```python
def fun(arr):
    n = len(arr)
    l = 0
    r = 0
    ans = 0
    state = ...
    while r < n:
        # update state of the current window with arr[r]
        ...

        # contract window until we have a valid one
        while True:
            if window is valid:
                break

            # update state of the current window with arr[l]
            ...

            # contract the window
            l += 1

        # update ans, e.g.:
        ans = max(ans, r - l + 1)

        # expand the window
        r += 1

    return ans
```

## Example

Given a binary array nums and an integer k, return the maximum number of consecutive 1's in the array if you can flip at most k 0's (https://leetcode.com/problems/max-consecutive-ones-iii).

A key insight here is that we can translate this question into returning the longest window that has <= k 0's, because then we can flip all the 0's to be 1's (this is a similar trick to https://leetcode.com/problems/max-consecutive-ones-ii/).

First, we solve it with brute force:

```python
def fun(arr, k):
	n = len(arr)
	ans = 0
	for l in range(n):
		for r in range(l, n):
			nz = 0
			for i in range(l, r + 1):
				if arr[i] == 0:
					nz += 1

			if nz <= k:
				ans = max(ans, r - l + 1)
	return ans
```

The time complexity is O(n^3) (it's very similar to https://leetcode.com/problems/maximum-subarray/). If the brute force solution looks like this and you want a O(n) solution, then consider the sliding window algorithm.

Now we apply the sliding window template:

```python
def fun(arr, k):
    n = len(arr)
    l = 0
    r = 0
    ans = 0
    nz = 0
    while r < n:
        # update state of the current window
        if arr[r] == 0:
            nz += 1

        # contract window until we have a valid one
        while nz == k+1:
            # update state of the current window
            if arr[l] == 0:
                nz -= 1
            l += 1

        ans = max(ans, r - l + 1)

        # expand the window
        r += 1

    return ans
```

Note that in the worst case the left pointer visits each element of the array once and the right pointer visits each element of the array once, so the time complexity is O(n).

## Example (2)

https://leetcode.com/problems/maximize-the-confusion-of-an-exam/

```python
def fun(arr, k):
    n = len(arr)
    l = 0
    r = 0
    ans = 0
    n_true = 0
    n_false = 0
    while r < n:
        # update state of the current window
        if arr[r] == 'T':
            n_true += 1
        else:
            n_false += 1
            
        # contract window until we have a valid one
        while n_true > k and n_false > k:
            # update state of the current window
            if arr[l] == 'T':
                n_true -= 1
            else:
                n_false -= 1
            l += 1
            
        ans = max(ans, r - l + 1)
        
        # expand the window
        r += 1
        
    return ans
```

## Other examples

* https://leetcode.com/problems/longest-substring-without-repeating-characters/

## Sources

* https://leetcode.com/tag/sliding-window/