"""Floyd-Warshall.

Dijkstra and Bellman-Ford are single source shortest path algorithms.
Floyd-Warshall is an all pairs shortest path algorithm. It applies to
graphs with positive or negative edge weights but with no negative
cycles.

Sources:
* https://en.wikipedia.org/wiki/Floyd%E2%80%93Warshall_algorithm
* https://leetcode.com/problems/find-the-city-with-the-smallest-number-of-neighbors-at-a-threshold-distance/solutions/490312/JavaC++Python-Easy-Floyd-Algorithm/
* http://web.archive.org/web/20230508143429/https://www.geeksforgeeks.org/floyd-warshall-algorithm-dp-16/
"""

def floyd_warshall(n, edges):
	d = [[float('inf')] * n for _ in range(n)]
	for i in range(n):
		d[i][i] = 0

	for u, v, w in edges:
		d[u][v] = w

	for k in range(n):
		for i in range(n):
			for j in range(n):
				d[i][j] = min(d[i][j], d[i][k] + d[k][j])
	return d


if __name__ == "__main__":
	n = 4
	edges = [
		[0, 3, 10],
		[0, 1, 5],
		[1, 2, 3],
		[2, 3, 1]
	]
	actual = floyd_warshall(n, edges)
	expected = [
		[0, 5, 8, 9],
		[float('inf'), 0, 3, 4],
		[float('inf'), float('inf'), 0, 1],
		[float('inf'), float('inf'), float('inf'), 0]
	]
	assert actual == expected

