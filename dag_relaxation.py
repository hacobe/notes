"""DAG relaxation.

Sources:
* https://ocw.mit.edu/courses/electrical-engineering-and-computer-science/6-006-introduction-to-algorithms-spring-2020/lecture-notes/MIT6_006S20_r10.pdf
* https://ocw.mit.edu/courses/electrical-engineering-and-computer-science/6-006-introduction-to-algorithms-spring-2020/lecture-notes/MIT6_006S20_r11.pdf
"""
def dfs_dag(Adj, s, order):
    for u in Adj[s]:
        dfs_dag(Adj, u, order)
    order.append(s)


def dag_relaxation(Adj, s, w):
    # "If the graph is acyclic, the order returned by dfs (or graph search)
    # is the reverse of a topological sort order."
    # (Recitation 10)
    order = []
    dfs_dag(Adj, s, order)
    order.reverse()

    # now order is the topological sort of the graph

    # We can prove the correctness of this algorithm via an inductive argument.
    # There is an edge from `u` to `v` for each `v` in `Adj[u]`.
    # Therefore, `u` is a parent of `v`, which implies that `u` comes before `v` in a topological sort.
    # Assume that all the `d[x]` for `x` that come before `v` in a topological sort gives the shortest distance between `s` and `x`.
    # By that assumption, `d[u]` gives the shortest distance between `s` and `u`.
    # We loop through all the edges between `u` and `v` and find the minimum `d[u] + w(u,v)`.
    # That minimum must be the shortest path between `s` and `v`.

    d = [float('inf') for _ in range(len(order))]
    d[s] = 0
    for u in order:
        for v in Adj[u]:
            if d[v] > d[u] + w(u, v):
                d[v] = d[u] + w(u, v)
    return d


if __name__ == "__main__":
    Adj = {}
    Adj[0] = [1]
    Adj[1] = [2, 5, 6]
    Adj[2] = [3]
    Adj[3] = [4]
    Adj[4] = [8]
    Adj[5] = [8]
    Adj[6] = [7]
    Adj[7] = [8]
    Adj[8] = []
    d = dag_relaxation(Adj, 0, lambda u, v: 1)
    print(d)
    assert d == [0, 1, 2, 3, 4, 2, 2, 3, 3, float("inf"), float("inf")]

