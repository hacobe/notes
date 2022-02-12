"""Dijkstra's shortest path algorithm."""
import heapq

def dijkstra(n, graph, start):
	visited = [False]*n
	d = [float("inf")] * n
	queue = []
	d[start] = 0
	heapq.heappush(queue, (0, start))
	while queue:
		g, u = heapq.heappop(queue)
		visited[u] = True
		for v, w in graph[u]:
			if visited[v]:
				continue
			f = g + w
			if f < d[v]:
				d[v] = f
				heapq.heappush(queue, (f, v))
	return d