# Eigendecomposition

We call $\textbf{v}$ an **eigenvector** of a square matrix $\textbf{A}$ if $\textbf{v}$ is nonzero and for some scalar $\lambda$ we have:

$\textbf{A} \textbf{v} = \lambda \textbf{v}$

We call $\lambda$ the **eigenvalue** of $\textbf{A}$.

A linear transformation acts on its eigenvectors like a scalar would. The eigenvalue is the factor by which the eigenvector is stretched (or squished) under the transformation.

Suppose that $\textbf{A}$ has $n$ linearly independent eigenvectors, then the **eigendecomposition** of $\textbf{A}$ is:

$\textbf{A} = \textbf{V} \textrm{diag}(\boldsymbol{\lambda}) \textbf{V}^{-1}$

where each column of $\textbf{V}$ is an eigenvector of $\textbf{A}$ and the $i$-th component of $\boldsymbol{\lambda}$ is the eigenvalue associated with the $i$-th column of $\textbf{V}$.

When $\textbf{A}$ is a real, symmetric matrix, then $\textbf{A}$ can be decomposed as follows:

$\textbf{A} = \textbf{Q} \boldsymbol{\Lambda} \textbf{Q}^T$

where each column of $\textbf{Q}$ is an eigenvector of $\textbf{A}$ and $\Lambda_{i,i}$ is the eigenvalue associated with the $i$-th column of $\textbf{Q}$. We can then interpret the original transformation as scaling the space by $\Lambda_{i,i}$ in the direction of the $i$-th column of $\textbf{Q}$.

One application of the eigendecomposition is to compute $\textbf{A}^n$ efficiently (https://math.stackexchange.com/questions/2628253/compute-the-100th-power-of-a-given-matrix).

## Sources

* Goodfellow, Deep learning, Section 2.7
* [Eigenvectors and eigenvalues](https://www.youtube.com/watch?v=PFDu9oVAE-g), 3Blue1Brown