# MinHashLSH

**MinHashLSH** consists of first applying the MinHash algorithm and then Locality Sensitive Hashing (LSH) as preprocessing steps for speeding up computations of pairwise similarities between sets. Applications include approximate deduplication and nearest neighbor search.

**MinHash** takes a corpus of N documents, where each document is represented as a set (e.g., the set of distinct words that appear in the document), and maps each document to an integer array of length K. These arrays have the special property that if H is the Hamming similarity between any 2 of the arrays, then H/K is approximately equal to the Jaccard similarity of the corresponding sets.

The **Hamming similarity** between 2 arrays of equal length is the number of positions at which the corresponding values in each array are equal.

The **Jaccard similarity** between 2 sets is the size of their intersection divided by the size of their union.

How does MinHash construct such an array for a set? It first maps the elements of the set to integers in a large range using, for example, CRC32 hashing. To get each of the K components of the array, it constructs a random hash function, hashes those integers and takes the minimum of the hash values as the value of the component. We map the elements of a set to a large range of integers before the random hashing in order to reduce the probability of collisions.

The random hash function is h(x) = (intercept + slope * x) % prime, where intercept and slope are random, non-negative integers less than the maximum possible value of x and prime is a prime number larger than the maximum possible value of x.

Why does the Hamming similarity divided by the length for 2 of these MinHash arrays approximately equal the Jaccard similarity?

Suppose we have the following 2 sets:

```
A = {1, 2, 5}
B = {2, 5, 9, 10}
```

We compute the union of the sets:

```
A u B = {1, 2, 5, 9, 10}
```

We then can write down a matrix representation of the 2 sets:

```
	  A B
1   1 0
2   1 1
5   1 1
9   0 1
10  0 1
```

Now suppose we shuffle the rows of this matrix. For example, we might get:

```
	  A B
2   1 1
1   1 0
10  0 1
5   1 1
9   0 1
```

The probability that the first row has a one in both columns is the equivalent to the probability that a randomly sampled row will have a one in both columns. The number of rows with a one in both columns is equal to |A n B| and the total number of rows is |A u B|, so the probability is |A n B|/|A u B|, i.e., the Jaccard similarity.

Here's an implementation:

```python
import numpy as np
np.random.seed(0)
A = set([1, 2, 5])
B = set([2, 5, 9, 10])
row_indices = sorted(list(A.union(B)))
mat = np.zeros((len(row_indices), 2))
for element in A:
	mat[row_indices.index(element), 0] = 1
for element in B:
	mat[row_indices.index(element), 1] = 1
K = 100000
H = 0
for _ in range(K):
	np.random.shuffle(mat)
	if mat[0,0] == 1 and mat[0,1] == 1:
		H += 1
prob = H/K
print(prob) # 0.40236
```

Now suppose we define `a` to be the array containing the indices of the rows in the shuffled matrix with a 1 in the A column in the same order as they appear in the shuffled matrix. And we define `b` in a similar way.

Using the shuffled matrix in the example above, we have:

```
a = [2, 1, 5]
b = [2, 10, 5, 9]
```

The probability that the first element of `a` equals the first element of `b` is equivalent to the probability that the first row of the shuffled matrix has a one in both columns. Why? The first row can either have a 1 in both columns or a 1 in one column and a 0 in the other column. If the first row has a 1 in both columns, then the first element of `a` and the first element of `b` are equal. Otherwise, the first element of `a` and the first element of `b` cannot be equal.

Instead of finding the first element of each array after shuffling by explicit construction, we can find it via hashing the elements of the set and taking the minimum.

Here's an implementation:

```python
A_list = [2, 1, 5]
B_list = [2, 10, 5, 9]
np.random.seed(0)
max_int = 2**32-1
prime = 4294967311 # prime number larger than max_int
assert prime > max_int
itoh = {x: np.random.randint(max_int) for x in row_indices}
assert len(set(itoh.values())) == len(itoh.values())
H = 0
for _ in range(K):
  intercept = np.random.randint(max_int)
  slope = np.random.randint(max_int)
  u = min([(intercept + slope * itoh[x]) % prime for x in A_list])
  v = min([(intercept + slope * itoh[x]) % prime for x in B_list])
  if u == v:
    H += 1
prob = H/K
print(prob) # 0.40299
```

The effect of using the MinHash representation to compute Jaccard similarity is to reduce the average time complexity from O(D), where D is the average size of the sets representing documents, to O(K), where K is the number of random hash function used. However, to find the nearest neighbor of a document, for example, we still need O(N) pairwise similarity computations. We may need to find the nearest neighbor of a document many times.

**LSH** is an approach to reducing the number of pairwise similarity computations. It precomputes a "neighbor dictionary" that maps from a document ID to a set of document IDs for documents that exceed some threshold of similarity with the key document. When we look for the nearest neighbor of a document, we look up the document in this dictionary and only compute similarity for the associated document IDs.

LSH takes as input the output of MinHash organized into a "signature matrix" with K rows (one for each random hash function) and a N columns (one for each document). The signature matrix is the transpose of the layout for the usual feature matrix.

LSH starts by dividing the signature matrix into b bands consisting of r rows each. For each band, we build a "band dictionary" that maps from a tuple of r integers to the set of column indices for columns in the band that contain those r integers in the same order as the tuple.[^1] Finally, we build the neighbor dictionary that maps from a column index to the all the column indices that appear together in at least one of the sets in at least one of the band dictionaries. 

Suppose we have the following signature matrix:

```
0 1 5 0 0
3 4 7 3 3
9 8 8 7 0
1 2 2 9 0
```

This implies we have 4 MinHash components and 5 documents.

We split up the signature matrix into 2 bands consisting of 2 rows each:

```
0 1 5 0 0
3 4 7 3 3
---------
9 8 8 7 0
1 2 2 9 0
```

Then we build the dictionary for the first band:

```python
band_dict1 = {
	(0, 3): {0, 1, 4},
	(1, 4): {1},
	(5, 7): {2}
}
```

And the dictionary for the second band:

```python
band_dict2 = {
	(9, 1): {0},
	(8, 2): {1, 2},
	(7, 9): {3},
	(0, 0): {4}
}
```

And finally the neighbor dictionary:

```python
band_dicts = [band_dict1, band_dict2]
neighbor_dict = collections.defaultdict(set)
for band_dict in band_dicts:
	for key in band_dict:
		for col_idx in band_dict[key]:
			neighbor_dict[col_idx].update(band_dict[key])

for col_idx in neighbor_dict:
	neighbor_dict[col_idx].discard(col_idx)

# {0: {1, 4}, 1: {0, 2, 4}, 4: {0, 1}, 2: {1}, 3: set()}
print(dict(neighbor_dict))
```

We can choose a threshold t of Jaccard similarity that defines how similar 2 documents have to be in order to be considered neighbors in the neighbor dictionary. For given threshold, we can choose a value of b (the number of bands) and r (the number of rows in each band) that minimizes the number of misclassifications of neighbors (see https://github.com/ekzhu/datasketch/blob/master/datasketch/lsh.py#L22). See 3.4.2 in MMDS for the analysis that underlies this procedure. Note that in the example above we chose r to be K/b, but r could be any integer in [1, K/b].

## Sources

* MMDS, Chapter 3, http://web.archive.org/web/20221225023101/http://infolab.stanford.edu/~ullman/mmds/ch3.pdf
* Section 4.2: "Approximate Matching with MinHash", [Deduplicating Training Data Makes Language Models Better](https://arxiv.org/pdf/2107.06499.pdf)

## Additional sources

* http://web.archive.org/web/20230115002411/https://mccormickml.com/2015/06/12/minhash-tutorial-with-python-code/
* https://stackoverflow.com/questions/4642172/computing-set-intersection-in-linear-time
* https://stackoverflow.com/questions/9755538/how-do-i-create-a-list-of-random-numbers-without-duplicates
* http://web.archive.org/web/20230115181450/http://matthewcasperson.blogspot.com/2013/11/minhash-for-dummies.html

[^1]: Taking a tuple of the r integers is only one way to construct the hash function. It is used [here](https://github.com/santurini/MinHash-LSH-From-Scratch/blob/main/functions.py#L226) and [here](https://github.com/colonialjelly/document-similarity/blob/master/docsim/lsh.py#L26). Another approach to convert the r integers to a single number as in [here](https://github.com/paschalischom/Minhash-LSH/blob/master/item_similarity.py#L198). datasketch has an optional argument for a hash function (https://github.com/ekzhu/datasketch/blob/master/datasketch/lsh.py#L111, https://github.com/ekzhu/datasketch/blob/master/datasketch/lsh.py#L169). Why does it do a bytes swap? See this issue (https://github.com/ekzhu/datasketch/issues/114).
