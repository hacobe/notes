# Smith-Waterman algorithm

The [note](https://github.com/hacobe/notes/blob/main/needleman_wunsch_algorithm.md) on the Needleman-Wunsch algorithm should be read before this note.

Given 2 strings s0 and s1, the Smith-Waterman algorithm returns an alignment of a substring of s0 and a substring of s1  that achieves the maximum alignment score over all the alignments of all the possible substring pairs.[^1]

Under the edit distance view of alignment, we can think of the algorithm as returning a sequence of operations that transforms a substring of s0 to a substring of s1. Furthermore, this sequence of operations achieves the maximum possible sum of operation scores over all the transformations between all the possible substring pairs. Using the edit distance as the score (gap_score=-1, mismatch_score=-1, match_score=0) returns 2 empty substrings, because it costs nothing to transform an empty substring into another empty substring. To avoid this trivial answer, we add a bonus for each successful match.

Smith-Waterman performs local sequence alignment as opposed to the global sequence alignment performed by the Needleman-Wunsch algorithm. It modifies Needleman-Wunsch so that a negative alignment score is replaced by 0. Also, instead of starting at the bottom right corner and tracing back to the top left corner, it starts at a cell that achieves the maximum value in the matrix and traces back until it hits a cell with value 0.

```python
import collections
import numpy as np

def g(s0, s1, n0, n1, gap_score=-2, match_score=1, mismatch_score=-1):
  mat = [[0 for _ in range(n1+1)] for _ in range(n0+1)]
  parents = collections.defaultdict(list)
  for m0 in range(1, n0+1):
    parents[(m0,0)] = [(m0-1,0)]
  for m1 in range(1, n1+1):
    parents[(0,m1)] = [(0,m1-1)]
  cells_global_max = [(0, 0)]
  global_max_value = 0
  for m0 in range(1, n0+1):
    for m1 in range(1, n1+1):
      last_move_down = max(0, mat[m0-1][m1] + gap_score)
      last_move_right = max(0, mat[m0][m1-1] + gap_score)
      last_move_diag = max(0, mat[m0-1][m1-1] + (match_score if s0[m0-1] == s1[m1-1] else mismatch_score))
      max_value = max(last_move_down, last_move_right, last_move_diag)
      mat[m0][m1] = max_value
      if last_move_diag == max_value:
        parents[(m0,m1)].append((m0-1, m1-1))
      if last_move_right == max_value:
        parents[(m0,m1)].append((m0, m1-1))
      if last_move_down == max_value:
        parents[(m0,m1)].append((m0-1, m1))
      
      if max_value > global_max_value:
        global_max_value = max_value
        cells_global_max = [(m0,m1)]
      elif max_value == global_max_value:
        cells_global_max.append((m0, m1))
    
  # Arbitrarily take the first cell that achieves
  # the global max.
  curr = cells_global_max[0]

  path = []
  while True:
    path.append(curr)

    end = False
    for parent in parents[curr]:
      if mat[parent[0]][parent[1]] == 0:
        path.append(parent)
        end = True
        break
    
    if end:
      break

    if len(parents[curr]) == 0:
      break

    # Break ties by taking the first parent.
    parent = parents[curr][0]
    curr = parent

  path.reverse()
  
  t0 = []
  t1 = []
  for i in range(1, len(path)):
    curr = path[i]
    prev = path[i-1]
    
    d0 = curr[0] - prev[0]
    d1 = curr[1] - prev[1]
    
    # Subtract by 1 because
    # we added a row and a column
    # to the matrix.
    i0 = curr[0]-1
    i1 = curr[1]-1

    if d0 == 1 and d1 == 1:
      t0.append(s0[i0])
      t1.append(s1[i1])
    elif d0 == 0:
      t0.append("-")
      t1.append(s1[i1])
    else:
      t0.append(s0[i0])
      t1.append("-")
      
  t0 = "".join(t0)
  t1 = "".join(t1)

  return global_max_value, mat, t0, t1

# An example from the "Smith-Waterman algorithm" Wikipedia page.
global_max_value, mat, t0, t1 = g(
	"GGTTGACTA", "TGTTACGG", 9, 8,
	gap_score=-2, match_score=3, mismatch_score=-3)
assert global_max_value == 13
assert (mat == np.array([
  [0, 0, 0, 0, 0, 0, 0, 0, 0],
  [0, 0, 3, 1, 0, 0, 0, 3, 3],
  [0, 0, 3, 1, 0, 0, 0, 3, 6],
  [0, 3, 1, 6, 4, 2, 0, 1, 4],
  [0, 3, 1, 4, 9, 7, 5, 3, 2],
  [0, 1, 6, 4, 7, 6, 4, 8, 6],
  [0, 0, 4, 3, 5, 10, 8, 6, 5],
  [0, 0, 2, 1, 3, 8, 13, 11, 9],
  [0, 3, 1, 5, 4, 6, 11, 10, 8],
  [0, 1, 0, 3, 2, 7, 9, 8, 7]
])).all()
assert t0 == "GTTGAC"
assert t1 == "GTT-AC"
```

## Sources

* http://web.archive.org/web/20230121232816/https://en.wikipedia.org/wiki/Smith%E2%80%93Waterman_algorithm
* http://web.archive.org/web/20230123195112/http://rna.informatik.uni-freiburg.de/Teaching/index.jsp?toolName=Smith-Waterman

[^1]: "The Smith-Waterman algorithm (Smith and Waterman, 1981) is a modification of Needleman-Wunsch for computing an optimal local alignment, i.e. the best global alignment of substrings of two input sequences." (https://academic.oup.com/bioinformatics/article/35/19/3547/5474902)