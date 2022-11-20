"""Dijkstra's shortest path algorithm."""
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
			if f < d[v]:
				d[v] = f
				heapq.heappush(heap, (f, v))
	return d