# Moore-Penrose pseudoinverse

Suppose we're given $\textbf{A}$ and $\textbf{y}$ and we want to solve for $\textbf{x}$ in the following system of linear equations:

$\textbf{A} \textbf{x} = \textbf{y}$

If $\textbf{A}$ is invertible, then we can do the following:

$\textbf{A}^{-1} \textbf{A} \textbf{x} = \textbf{A}^{-1} \textbf{y}$

$\textbf{x} = \textbf{A}^{-1} \textbf{y}$

If $\textbf{A}$ is not invertible, then we can use the Moore-Penrose pseudoinverse $\textbf{A}^+$.

If $\textbf{A}$ is not invertible, because it has more columns than rows, i.e., more unknowns than equations, then there are usually an infinite number of $\textbf{x}$ that satisfy the equations. In this case, $\textbf{x} = \textbf{A}^+ \textbf{y}$ gives the solution with minimal Euclidean norm among all possible solutions.

If $\textbf{A}$ is not invertible, because it has more rows than columns, i.e., more equations than unknowns, then there are usually no solutions. In this case, $\textbf{x} = \textbf{A}^+ \textbf{y}$ gives the $\textbf{x}$ that minimizes $\lVert \textbf{A} \textbf{x} - \textbf{y} \rVert_2$.

We compute the Moore-Penrose pseudoinverse by first computing the SVD of $\textbf{A} = \textbf{U} \textbf{D} \textbf{V}^T$ and then computing $\textbf{A}^+ = \textbf{V} \textbf{D}^+ \textbf{U}^T$, where "the pseudoinverse $\textbf{D}^+$ of a diagonal matrix $\textbf{D}$ is obtained by taking the reciprocal of its nonzero elements then taking the transpose of the resulting matrix" (Goodfellow).

## Sources

* Goodfellow, Deep learning, Section 2.9
* https://en.wikipedia.org/wiki/Overdetermined_system