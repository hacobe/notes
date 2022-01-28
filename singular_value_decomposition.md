# Singular value decomposition

Every real matrix has a singular value decomposition (SVD).

The SVD takes a $m \times n$ matrix $\textbf{A}$ and decomposes it as follows:

$\textbf{A} = \textbf{U} \textbf{D} \textbf{V}^T$

where $\textbf{U}$ is a $m \times m$ orthogonal matrix, $\textbf{D}$ is a $m \times n$ diagonal matrix and $\textbf{V}$ is a $n \times n$ orthogonal matrix.

The columns of $\textbf{U}$ are called the left-singular vectors, the columns of $\textbf{V}$ are called the right-singular vectors and the values along the diagonal of $\textbf{D}$ are called the singular values.

The left-singular vectors are actually the eigenvectors of $\textbf{A} \textbf{A}^T$, the right-singular vectors are the eigenvectors of $\textbf{A}^T \textbf{A}$ and the nonzero singular values are the square roots of the eigenvalues of $\textbf{A}^T \textbf{A}$ (and of $\textbf{A} \textbf{A}^T$).

## Sources

* Goodfellow, Deep learning, Section 2.8
* https://gregorygundersen.com/blog/2018/12/10/svd/