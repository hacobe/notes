"""Bellman-Ford

Sources:
* https://ocw.mit.edu/courses/electrical-engineering-and-computer-science/6-006-introduction-to-algorithms-spring-2020/lecture-notes/MIT6_006S20_r12.pdf
"""
def bellman_ford(Adj, n, w, s):
    d = [float("inf") for _ in range(n)]
    d[s] = 0
    for _ in range(n-1):
        for u in range(n):
            for v in Adj[u]:
                if d[v] > d[u] + w(u, v):
                    d[v] = d[u] + w(u, v)

    for u in range(n):
        for v in Adj[u]:
            if d[v] > d[u] + w(u,v):
                raise Exception("Negative weight cycle")
    return d