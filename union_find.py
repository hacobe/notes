"""Union-Find data structure.

	  1         3
	 /         /  \
	0         4 -- 5
	 \
	  2

To build the Union-Find data structure, we initialize
a root array so that root[i] = i and a rank array so that
rank[i] = 1.

root = [0, 1, 2, 3, 4, 5]
rank = [1, 1, 1, 1, 1, 1]

This represents a set for each vertex:

{0}, {1}, {2}, {3}, {4}, {5}

root[i] gives the "root" of the set of which the vertex
i is a member. rank[i] gives the size of the set of which
vertex is a member.

The graph above consists of the following edges:

edges = [[0,1],[0,2],[3,5],[5,4],[4,3]]

We add each edge to the data structure.

We start with the first edge from vertex 0 to vertex 1.

We get the root of each vertex.

The root of vertex 0 is vertex 0 and the root of
vertex 1 is vertex 1.

We choose one of them as the new root.

In particular, we choose the one with larger rank
(i.e., the one from the larger set).
If they have the same rank, then we arbitrarily
choose the root associated with the destination
vertex of the edge.

In this case, they have the same rank, so we choose
vertex 1 as the new root. We set the root of vertex 0 to
1.

We also increment the rank of vertex 1 (the chosen root)
by the rank of vertex 0 (the unchosen root).

root = [1, 1, 2, 3, 4, 5]
rank = [1, 2, 1, 1, 1, 1]

In this way, we union the set {0} with vertex 0 as the
root and the set {1} with vertex 1 as the root to create
the set {0, 1} with vertex 1 as the root.

We then add the second edge from vertex 0 to vertex 2.

The root of vertex 2 is vertex 2 with rank 1. The root
of vertex 0 is vertex 1 with rank 2, so we take vertex 1
as the new root.

root = [1, 1, 1, 3, 4, 5]
rank = [1, 3, 1, 1, 1, 1]	

We then add the third edge from vertex 3 to vertex 5.

root = [1, 1, 1, 5, 4, 5]
rank = [1, 3, 1, 1, 1, 2]

Then the fourth edge from vertex 5 to vertex 4.

root = [1, 1, 1, 5, 5, 5]
rank = [1, 3, 1, 1, 1, 3]

And the last edge from vertex 4 to vertex 3.

The root of vertex 4 is vertex 5. The root of vertex 3
is also vertex 5, so we do not perform any updates on
the arrays.

We now have the 2 connected components:
{0, 1, 2} and {3, 4, 5}.

Having built the Union-Find data structure, we can
check a destination vertex is reachable from a source
vertex by checking if they have the same root.

Sources:
* https://leetcode.com/problems/find-if-path-exists-in-graph/solutions/2715942/find-if-path-exists-in-graph/
"""

class UnionFind:

	def __init__(self, n):
		self.root = list(range(n))
		self.rank = [1] * n

	def find(self, u):
		if u == self.root[u]:
			return u
		return self.find(self.root[u])

	def union(self, u, v):
		root_u, root_v = self.find(u), self.find(v)
		if root_u != root_v:
			# Of (root_u, root_v), make root_v
			# the one with the largest rank.
			if self.rank[root_u] > self.rank[root_v]:
				root_u, root_v = root_v, root_u
			# Take the one with largest rank as the root.
			self.root[root_u] = root_v
			self.rank[root_v] += self.rank[root_u]


def validPath(n, edges, source, destination):
	# Preprocessing.
	uf = UnionFind(n)
	for u, v in edges:
		uf.union(u, v)
	# Check for valid path.
	return uf.find(source) == uf.find(destination)


if __name__ == "__main__":
	edges = [[0,1],[0,2],[3,5],[5,4],[4,3]]
	assert validPath(6, edges, 0, 5) == False
