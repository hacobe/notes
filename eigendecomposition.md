# Eigendecomposition

We call $\textbf{v}$ an **eigenvector** of a square matrix $\textbf{A}$ if $\textbf{v}$ is nonzero and for some scalar $\lambda$ we have:

$\textbf{A} \textbf{v} = \lambda \textbf{v}$

We call $\lambda$ the **eigenvalue** of $\textbf{A}$.

A linear transformation acts on its eigenvectors like a scalar would. The eigenvalue is the factor by which the eigenvector is stretched (or squished or flipped) under the transformation.

It turns out that every real, symmetric matrix $\textbf{A}$ can be decomposed as follows:

$\textbf{A} = \textbf{Q} \Lambda \textbf{Q}^T$

where $\textbf{Q}$ is an orthogonal matrix composed of the eigenvectors of $\textbf{A}$ and $\Lambda$ is a diagonal matrix where $\Lambda_{i,i}$ is the eigenvalue associated with the eigenvector given by the $i$-th column of $\textbf{Q}$. This is called the **eigendecomposition** of $\textbf{A}$. We can then interpret the original transformation as scaling the space by $\Lambda_{i,i}$ in the direction of the $i$-th column of $\textbf{Q}$.

One application of the eigendecomposition is to compute $\textbf{A}^n$ efficiently, because $\textbf{A}^n = \textbf{Q} \Lambda^n \textbf{Q}^T$ and $\Lambda$ is a diagonal matrix.

## Sources

* Goodfellow, Deep learning, Section 2.7
* [Eigenvectors and eigenvalues](https://www.youtube.com/watch?v=PFDu9oVAE-g), 3Blue1Brown