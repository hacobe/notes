# Needleman-Wunsch algorithm

## Introduction

An "alignment" of 2 strings s0 and s1 consists of 2 strings t0 and t1 that have the same length and are obtained by lining up the characters of s0 and s1 with the option to insert a "gap" at any position in each of the strings (including at the beginning or end) as long as there is not a gap at the same position in both strings. We assume that s0 and s1 do not contain any hyphens so that we can represent gaps in t0 and t1 with hyphens.

For example, suppose we have:

```
s0 = GATCGGCAT
s1 = CAATGTGAATC
```

One possible alignment is:

```
t0 = G-ATCG-GCAT-
t1 = CAAT-GTGAATC
```

The idea is to use the alignment to identify regions of similarity in the 2 strings. To this end, we assign a score to each position of the alignment. For example:

* +1 if t0[i] == t1[j]
* -1 if t0[i] != '-' and t1[j] != 'i' and t0[i] != t1[j]
* -2 if t0[i] == '-' or t1[j] == '-'

We then compute the alignment score as the sum of the position scores. The alignment score for the alignment above is (-1) + (-2) + (1) + (1) + (-2) + (1) + (-2) + (1) + (-1) + (1) + (1) + (-2) = -4.

Given 2 strings, the **Needleman-Wunsch algorithm** returns an alignment that achieves the maximum alignment score using dynamic programming.

## Edit Distance view of alignment

We can think of an alignment as representing a sequence of operations on s0 to build up a string that equals s1 or as a sequence of operations to transform s0 into s1. The code below performs operations on s0 to build up a string z that equals s1 at termination and prints out the operations required to transform s0 into s1 along the way:

```python
def transform(s0, s1, t0, t1):
  assert len(t0) == len(t1)

  i = j = k = 0
  z = [""] * len(s1)
  for k in range(len(t0)):
    if t0[k] == t1[k]:
      z[j] = s0[i]
      i += 1
      j += 1
    elif t0[k] != t1[k] and t0[k] != '-' and t1[k] != '-':
      print(f"Replace '{s0[i]}' with '{t1[k]}' at position {j}")
      z[j] = t1[k]
      i += 1
      j += 1
    elif t0[k] == '-':
      print(f"Insert '{t1[k]}' at position {j}")
      z[j] = t1[k]
      j += 1
    elif t1[k] == '-':
      print(f"Delete '{s0[i]}' at position {j}")
      i += 1
    else:
      raise ValueError("Invalid t0 and t1")
  return "".join(z)

assert transform("GATCGGCAT", "CAATGTGAATC", "G-ATCG-GCAT-", "CAAT-GTGAATC") == "CAATGTGAATC"
```

It prints out the following lines:

```
Replace 'G' with 'C' at position 0
Insert 'A' at position 1
Delete 'C' at position 4
Insert 'T' at position 5
Replace 'C' with 'A' at position 7
Insert 'C' at position 10
```

We can check that these operations indeed transform s0 into s1:

```
Replace 'G' with 'C' at position 0
GATCGGCAT -> CATCGGCAT
Insert 'A' at position 1
CATCGGCAT -> CAATCGGCAT
Delete 'C' at position 4
CAATCGGCAT -> CAATGGCAT
Insert 'T' at position 5
CAATGGCAT -> CAATGTGCAT
Replace 'C' with 'A' at position 7
CAATGTGCAT -> CAATGTGAAT
Insert 'C' at position 10
CAATGTGAAT -> CAATGTGAATC
```

## Matrix view of alignment

Another way to think of alignment is as a path from the upper left hand corner to the bottom right hand corner of a matrix where the rows correspond to characters in s0 and the columns correspond to characters in s1 (with one additional row and column to allow for insertion or deletion at the beginning of a string). At each step, we can either move (i) a cell to the right, (ii) a cell down or (iii) diagonally (one cell down and one cell to the right). (i) is a hyphen in t0, (ii) is a hyphen into t1 and (iii) is either a match or mismatch that does not involve hyphens.

Here is the path formed for the alignment above:

```
 _CAATGTGAATC
_*
G **
A   *
T    *
C    *
G     **
G       *
C        *
A         *
T          **
```

As an aside, the number of possible alignments is given by the Delannoy number D(n0, n1). The number can be computed via the recurrence relation D(n0, n1) = D(n0 - 1, n1) + D(n0, n1 - 1) + D(n0 - 1, n1 - 1) if n0 >= 1 and n1 >= 1 and 1 otherwise. There is also a closed form solution. See [here](https://math.stackexchange.com/questions/1814693/counting-number-of-distinct-paths-if-diagonal-move-is-allowed-along-horizontal-a) and [here](http://web.archive.org/web/20230120224123/https://en.wikipedia.org/wiki/Delannoy_number) for details.

# Computing the maximum alignment score

Let f(s0, s1, n0, n1) be the function that returns the maximum alignment score for input strings s0[:n0] and s1[:n1].

The idea will be to define a matrix M like the one above, where M[m0, m1] = the maximum alignment score for s0[:m0] and s1[:m1] so that the cell in the bottom right corner contains the return value for f(s0, s1, n0, n1). Suppose we have arrived at that bottom right corner cell. We could have got there from the cell directly to its left, the cell directly above it, or from the cell directly above and to the left of it. A naive solution is to use this fact to recurse on the cell coordinates:

```python
def f(s0, s1, n0, n1, gap_score=-2, match_score=1, mismatch_score=-1):
  if n0 == 0 or n1 == 0:
    return gap_score * max(n0, n1)
  last_move_down = g(s0, s1, n0-1, n1) + gap_score
  last_move_right = g(s0, s1, n0, n1-1) + gap_score
  last_move_diag = g(s0, s1, n0-1, n1-1) + (match_score if s0[n0-1] == s1[n1-1] else mismatch_score)
  return max(last_move_down, last_move_right, last_move_diag)
```

This approach has O(3^max(n0, n1)) worst case time complexity.

A more efficient approach is to use dynamic programming:

```python
def f(s0, s1, n0, n1, gap_score=-2, match_score=1, mismatch_score=-1, reduce_fn=max):
  if n0 == 0 or n1 == 0:
    return gap_score * max(n0, n1)
  mat = [[0 for _ in range(n1+1)] for _ in range(n0+1)]
  for m0 in range(1, n0+1):
    mat[m0][0] = gap_score * m0
  for m1 in range(1, n1+1):
    mat[0][m1] = gap_score * m1
  for m0 in range(1, n0+1):
    for m1 in range(1, n1+1):
      last_move_down = mat[m0-1][m1] + gap_score
      last_move_right = mat[m0][m1-1] + gap_score
      last_move_diag = mat[m0-1][m1-1] + (match_score if s0[m0-1] == s1[m1-1] else mismatch_score)
      mat[m0][m1] = reduce_fn(last_move_down, last_move_right, last_move_diag)
  return mat[n0][n1]
```
 
We can also use the function above to solve the [edit distance problem](https://leetcode.com/problems/edit-distance/description/) if we set the gap_score to 1, the match_score to 0, the mismatch_score to 1 and the reduce_fn to min.

# Finding an alignment that achieves the maximum score

How do we get an alignment that achieves the maximum possible alignment score?

We add parent pointers at each step and then traverse those pointers to recover the path through the matrix:

```python
def g(s0, s1, n0, n1, gap_score=-2, match_score=1, mismatch_score=-1, comp_fn=lambda x, y: x > y):
  if n0 == 0 or n1 == 0:
    return gap_score * max(n0, n1)
  parents = {}
  mat = [[0 for _ in range(n1+1)] for _ in range(n0+1)]
  for m0 in range(1, n0+1):
    mat[m0][0] = gap_score * m0
  for m1 in range(1, n1+1):
    mat[0][m1] = gap_score * m1
  for m0 in range(1, n0+1):
    for m1 in range(1, n1+1):
      prev_cell_to_score = {
          (m0-1, m1): mat[m0-1][m1] + gap_score,
          (m0, m1-1): mat[m0][m1-1] + gap_score,
          (m0-1, m1-1): mat[m0-1][m1-1] + (match_score if s0[m0-1] == s1[m1-1] else mismatch_score)
      }
      prev_cell_best = None
      best_score = None
      for prev_cell in prev_cell_to_score.keys():
        score = prev_cell_to_score[prev_cell]
        if best_score is None or comp_fn(score, best_score):
          best_score = score
          prev_cell_best = prev_cell
      mat[m0][m1] = best_score
      parents[(m0, m1)] = prev_cell_best

  curr = (n0, n1)
  path = []
  while curr != (0, 0):
    path.append(curr)
    parent = parents[curr]
    curr = parent
  path.append((0, 0))
  path.reverse()

  prev = path[0]
  t0 = []
  t1 = []
  for i in range(1, len(path)):
    curr = path[i]
    prev = path[i-1]

    d1 = curr[0] - prev[0]
    d2 = curr[1] - prev[1]
    
    if d1 == 1 and d2 == 1:
      t0.append(s0[prev[0]])
      t1.append(s1[prev[1]])
    elif d1 == 0:
      t0.append("-")
      t1.append(s1[prev[1]])
    else:
      t0.append(s0[prev[0]])
      t1.append("-")

  t0 = "".join(t0)
  t1 = "".join(t1)

  return mat[n0][n1], t0, t1
```

Running the function above for s0 and s1, we get a maximum score of -3 and the following alignment:

```
GATCG-GCAT-
CAATGTGAATC
```

We can double check the alignment score: (-1) + (1) + (-1) + (-1) + (1) + (-2) + (1) + (-1) + (1) + (1) + (-2) = -3.

## Sources

* http://web.archive.org/web/20230120195430/https://en.wikipedia.org/wiki/Needleman%E2%80%93Wunsch_algorithm
* http://web.archive.org/web/20230120195410/https://ocw.mit.edu/ans7870/6/6.047/f15/MIT6_047F15_Compiled.pdf
* CLRS, Pgs, 366-367: "The edit-distance problem is a generalization of the problem of aligning two DNA sequences...One such method to align two sequences x and y consists of inserting spaces at arbitrary locations in the two sequences (including at either end) so that the resulting sequences x' and y' have the same length but do not have a space in the same position (i.e., no position j are both x'[j] and y'[j] a space.) Then assign a 'score' to each position..."
* http://web.archive.org/web/20230120195528/http://melvinacunaalgorithms.blogspot.com/2016/10/edit-distance.html: "For the optimal alignment only the copy, replace, delete and insert operations are needed. Insert and delete is used for a position with a score of * (For insert the white space will end up in x' and for delete in y'). Copy is used for a position with a score of +. Replace is used for a position with a score of -."
* http://web.archive.org/web/20230121160824/https://gist.github.com/slowkow/06c6dba9180d013dfd82bec217d22eb5