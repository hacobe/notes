"""Dijkstra's shortest path algorithm.

Here is a physics analogy for Dijkstra's algorithm:[^1]
"Let's say that each node of a graph is represented by a sphere.
 Two spheres are connected by a thread if and only if there is an edge between them in a graph.
 The lengths of these threads are directly proportional to the weight of the corresponding edges.
 All of these spheres are laying on the exact same spot on the ground.
 We pick up the sphere that corresponds to the starting node and as it goes up, it pulls the other spheres with it.
 The spheres leave the ground one by one, and the shortest distance between them and
 the starting sphere is a straight line distance between them.
 In terms of Dijkstra's algorithm, this is what we actually do:
 We've got two groups of spheres - the ones on the ground and the ones that have already been lifted.
 In each iteration, we pick up one of the spheres from the ground and calculate their distance from the first sphere."

Here is another analogy:[^2]
"Suppose we drop a huge colony of ants onto the source node u at time 0.
 They split off from there and follow all possible paths through the graph at a rate of one unit per second.
 Then the first ant who finds the target node v will do so at time d(u, v) seconds,
 where d(u, v) is the shortest distance from u to v. How do we find when that is?
 We just need to watch the expanding wavefront of ants."

[^1]: https://stackabuse.com/courses/graphs-in-python-theory-and-implementation/lessons/dijkstras-algorithm-vs-a-algorithm/
[^2]: https://www.quora.com/What-is-the-simplest-intuitive-proof-of-Dijkstra%E2%80%99s-shortest-path-algorithm
"""
import heapq

def dijkstra(n, graph, start):
	visited = [False]*n
	d = [float("inf")] * n
	heap = []
	d[start] = 0
	heapq.heappush(heap, (0, start))
	while heap:
		g, u = heapq.heappop(heap)
		visited[u] = True
		for v, w in graph[u]:
			if visited[v]:
				continue
			f = g + w
			if d[v] > f:
				d[v] = f
				heapq.heappush(heap, (f, v))
	return d