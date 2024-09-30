# Sliding window

Suppose we're given a non-empty array of n integers and we want to compute the maximum sum of a subarray of length k (https://www.geeksforgeeks.org/problems/max-sum-subarray-of-size-k5313/1).

Here is a brute force solution:

```python
def fun(arr, k):
    n = len(arr)
    max_s = arr[0]
    for start in range(n):
        if start + k > n:
            continue
        s = 0
        for i in range(start, start + k):
            s += arr[i]
        max_s = max(max_s, s)
    return max_s
```

The time complexity is O(nk).

An optimized solution is to place a window of length k at the start of the array and compute the sum of the integers that fall into the window. We then slide the window a step to the right at a time. At each step, one integer leaves the window and one integer enters the window and we adjust the sum accordingly without having to recompute the sum. Here is the optimized solution:

```python
def fun(arr, k):
    n = len(arr)
    l = 0
    r = k-1
    s = 0
    for i in range(l, r+1):
        s += arr[i]
    max_s = s
    for l in range(1, n):
        r = l + k - 1
        if r >= n:
            break
        s -= arr[l-1]
        s += arr[r]
        max_s = max(max_s, s)
    return max_s
```

The time complexity is O(n).

This is the **fixed sliding window** technique.

Here's a similar example.

Suppose we are given a string consisting of lowercase English letters and an integer k and we want to compute the number of substrings of length k with no repeated characters (https://leetcode.com/problems/find-k-length-substrings-with-no-repeated-characters). Assume k >> 26.

Here is a naive solution:

```python
def has_repeated_chars(char_freqs):
    for c in range(len(char_freqs)):
        if char_freqs[c] >= 2:
            return True
    return False

def fun(s, k):
    ans = 0
    n = len(s)
    for start in range(n):
        if start + k > n:
            break
        char_freqs = [0 for _ in range(26)]
        for i in range(start, start + k):
            char_freqs[ord(s[i])-ord('a')] += 1
        if not has_repeated_chars(char_freqs):
            ans += 1
    return ans
```

The time complexity is O(nk).

An optimized solution is to place a window of length k at the start of the string and compute the character frequency of the characters that fall into the window. We then slide the window a step to the right at a time. At each step, one character leaves the window and one character enters the window and we adjust the character frequency accordingly without having to recompute it. Here is the optimized solution:

```python
def has_repeated_chars(char_freqs):
    for c in range(len(char_freqs)):
        if char_freqs[c] >= 2:
            return True
    return False

def fun(s, k):
    n = len(s)
    if n < k:
        return 0

    l = 0
    r = k-1
    char_freqs = [0 for _ in range(26)]
    for i in range(l, r+1):
        char_freqs[ord(s[i])-ord('a')] += 1

    ans = 0
    if not has_repeated_chars(char_freqs):
        ans += 1

    for l in range(1, n):
        r = l + k - 1
        if r >= n:
            break
        char_freqs[ord(s[l-1])-ord('a')] -= 1
        char_freqs[ord(s[r])-ord('a')] += 1
        if not has_repeated_chars(char_freqs):
            ans += 1

    return ans
```

The time complexity is O(n).

Suppose now we're given a string consisting of lowercase English letters and we want to compute the number of substrings of any length with no repeated characters (https://leetcode.com/problems/count-substrings-without-repeating-character).

Here is a brute force solution:

```python
def has_repeated_chars(char_freqs):
    for c in range(len(char_freqs)):
        if char_freqs[c] >= 2:
            return True
    return False

def fun(s):
    ans = 0
    n = len(s)
    for l in range(n):
        for r in range(l, n):
            char_freqs = [0 for _ in range(26)]
            for i in range(l, r+1):
                char_freqs[ord(s[i])-ord('a')] += 1
            if not has_repeated_chars(char_freqs):
                ans += 1
    return ans
```

The time complexity is O(n^3).

Here's an optimized solution. For each index r, find the longest possible substring ending at r that has no repeated characters.

```python
def has_repeated_chars(char_freqs):
    for c in range(len(char_freqs)):
        if char_freqs[c] >= 2:
            return True
    return False

def fun(s):
    ans = 0
    n = len(s)
    l = 0
    char_freqs = [0 for _ in range(26)]
    for r in range(n):
        char_freqs[ord(s[r])-ord('a')] += 1

        # we stop as soon as we can to get the longest possible substring.
        while has_repeated_chars(char_freqs):
            char_freqs[ord(s[l])-ord('a')] -= 1
            l += 1

        assert not has_repeated_chars(char_freqs)

        # we're now at the longest possible substring ending at r.
        # we count only this substring, but also all of the substrings
        # of the substring, because if a substring has no repeated characters
        # then neither do any of its substrings.
        ans += r - l + 1
    return ans
```

The left pointer touches each character at most once and the right character touches each character at most once, so the time complexity is O(n).

Note that computing the maximum sum of a subarray of any length (https://leetcode.com/problems/maximum-subarray/) is not tagged as a sliding window problem. 

This is the **variable sliding window** technique.

Here's pseudocode for this technique:

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

## Example (3)

https://leetcode.com/problems/count-of-substrings-containing-every-vowel-and-k-consonants-ii/

We first solve it using brute force:

```python
def has_all_the_vowels(vowel_to_count):
    for count in vowel_to_count.values():
        if count == 0:
            return False
    return True

def fun(word, k):
    n = len(word)
    n_substrings_with_k_consonants_and_all_the_vowels = 0
    for l in range(n):
        for r in range(l, n):
            vowel_to_count = {"a": 0, "e": 0, "i": 0, "o": 0, "u": 0}
            n_consonants = 0
            for i in range(l, r+1):
                if word[i] in vowel_to_count:
                    vowel_to_count[word[i]] += 1
                else:
                    n_consonants += 1

            has_k_consonants_and_all_the_vowels = (n_consonants == k) and has_all_the_vowels(vowel_to_count)
            if has_k_consonants_and_all_the_vowels:
                n_substrings_with_k_consonants_and_all_the_vowels += 1

    return n_substrings_with_k_consonants_and_all_the_vowels
```

It's not immediately clear how to apply to optimize this brute force solution. We simplify the problem to just counting the number of substrings that contain all the vowels:

```python
def has_all_the_vowels(vowel_to_count):
    for count in vowel_to_count.values():
        if count == 0:
            return False
    return True

def fun(word):
    n = len(word)
    n_substrings_with_all_the_vowels = 0
    for l in range(n):
        for r in range(l, n):
            vowel_to_count = {"a": 0, "e": 0, "i": 0, "o": 0, "u": 0}
            for i in range(l, r+1):
                if word[i] in vowel_to_count:
                    vowel_to_count[word[i]] += 1

            if has_all_the_vowels(vowel_to_count):
                n_substrings_with_all_the_vowels += 1

    return n_substrings_with_all_the_vowels
```

We could also count the number of substrings that do not contain all the vowels and then subtract that from the total number of substrings:

```python
def has_all_the_vowels(vowel_to_count):
    for count in vowel_to_count.values():
        if count == 0:
            return False
    return True

def fun(word):
    n = len(word)
    n_substrings_without_all_the_vowels = 0
    for l in range(n):
        for r in range(l, n):
            vowel_to_count = {"a": 0, "e": 0, "i": 0, "o": 0, "u": 0}
            for i in range(l, r+1):
                if word[i] in vowel_to_count:
                    vowel_to_count[word[i]] += 1
            if not has_all_the_vowels(vowel_to_count):
                n_substrings_without_all_the_vowels += 1

    n_substrings = (n * (n + 1)) // 2
    return n_substrings - n_substrings_without_all_the_vowels
```

We can now optimize this by finding the longest substring without all the vowels and ending at r for each index r:

```python
def has_all_the_vowels(vowel_to_count):
    for count in vowel_to_count.values():
        if count == 0:
            return False
    return True

def fun(word):
    n = len(word)
    n_substrings_without_all_the_vowels = 0
    l = 0
    vowel_to_count = {"a": 0, "e": 0, "i": 0, "o": 0, "u": 0}
    for r in range(n):
        if word[r] in vowel_to_count:
            vowel_to_count[word[r]] += 1

        while has_all_the_vowels(vowel_to_count):
            if word[l] in vowel_to_count:
                vowel_to_count[word[l]] -= 1
            l += 1

        assert not has_all_the_vowels(vowel_to_count)
        n_substrings_without_all_the_vowels += r - l + 1

    n_substrings = (n * (n + 1)) // 2
    return n_substrings - n_substrings_without_all_the_vowels
```

Now we extend this function to finding the longest substring without all the vowels or with at most k consonants. If a substring does not have all the vowels or has at most k consonants, then all of its substrings will not have all the vowels or will have have at most k consonants.

```python
def has_all_the_vowels(vowel_to_count):
    for count in vowel_to_count.values():
        if count == 0:
            return False
    return True

def helper(word, k):
    n = len(word)
    ans = 0
    l = 0
    vowel_to_count = {"a": 0, "e": 0, "i": 0, "o": 0, "u": 0}
    n_consonants = 0
    for r in range(n):
        if word[r] in vowel_to_count:
            vowel_to_count[word[r]] += 1
        else:
            n_consonants += 1

        while has_all_the_vowels(vowel_to_count) and n_consonants > k:
            if word[l] in vowel_to_count:
                vowel_to_count[word[l]] -= 1
            else:
                n_consonants -= 1
            l += 1

        v = has_all_the_vowels(vowel_to_count)
        assert (not v) or (n_consonants <= k)
        a = v and (n_consonants > k)
        b = v and (n_consonants <= k)
        c = (not v) and (n_consonants <= k)
        d = (not v) and (n_consonants > k)
        bc = n_consonants <= k
        assert b or c or d
        assert bc or d
        assert not a
        ans += r - l + 1

    return ans

def fun(word, k):
    # no. of substrings with at most k consonants
    # + no. of substrings without all the vowels and more than k consonants
    # - no. of substrings with at most k-1 consonants
    # - no. of substrings without all the vowels and more than k-1 consonants
    # = 
    # no. of substrings with k consonants
    # - no. of substrings with k consonants and without all the vowels
    # =
    # no. of substrings with k consonants with all the vowels
    return helper(word, k) - helper(word, k-1)
```

## Sources

* https://leetcode.com/tag/sliding-window/