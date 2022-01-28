# 3Blue1Brown's Linear Algebra series

## Vectors

A **scalar** $x$ is a single number.

A **vector** is an array of numbers. You can think of it as an arrow with the tail rooted at the origin and the head at the point given by the coordinates of the array of numbers that define the vector. An arrow has a direction and a magnitude.

There are 2 basic operations on vectors:

* Vector addition: To add a vector $\textbf{a}$ and a vector $\textbf{b}$, root $\textbf{a}$ at the origin and root $\textbf{b}$ at the head of $\textbf{a}$. Then draw a vector rooted at the origin to the head of $\textbf{b}$. That vector is the sum.
* Scalar multiplication: Streching (multiplying by a positive number), squishing (multiplying by a fraction), reversing the direction (multiplying by a negative number) of a vector or collapsing the vector to the origin by multiplying by 0.

## Linear combinations, span and basis vectors

Consider a vector in 2D.

The x-coordinate of the vector is a scalar that scales $\hat{i}$ (the unit vector in the x-direction) and the y-coordinate of the vector is a scalar that scales $\hat{j}$ (the unit vector in the y-direction).

The vector is a sum of 2 scaled vectors. $\hat{i}$ and $\hat{j}$ are the "basis vectors" (we could choose other basis vectors).

The sum of scaled vectors is called a **linear combination** of those vectors.

The **span** of a set of vectors is the set of all their linear combinations. It answers: what are the all the possible places you can reach using only vector addition and scalar multiplication?

If you think about a vector alone, think about the arrow. If you think about a set of vectors, think about them as points (or the geometrical object that those points make like a line or a plane).

What does the span of 2 vectors that point in different directions in 3D space look like? It will be a plane that cuts through 3D space.

A set of vectors is **linearly independent** if no vector in the set is a linear combination of the other vectors.

The **basis** of a space is the set of linearly independent vectors that span that space.

## Linear transformations and matrices

Transformation evokes movement. Think of taking an input vector and moving it to create some output vector. We can imagine each possible input vector moving to its corresponding output vector and how that transforms the space. Or we watch every point in space move to some other point. A way to visualize this is the grid in the plane getting streched or squeezed and rotated.

A linear transformation is one in which all grid lines remain parallel and evenly spaced and the origin remains in the same place.

Consider a 2D vector $\textbf{v}$. You can deduce where it goes under the transformation based on just where $\hat{i}$ and $\hat{j}$ end up. The vector $\textbf{v}$ starts as a linear combination of $\hat{i}$ and $\hat{j}$ and after the transformation, it's a linear combination of the transformed $\hat{i}$ and $\hat{j}$ with the same coefficients. Therefore, a linear transformation is completely described by just 4 numbers (where $\hat{i}$ and $\hat{j}$ end up).

A 2x2 matrix gives a linear transformation where the first column gives the coordinates of where $\hat{i}$ lands in the transformation and the second column gives the coordinates of where $\hat{j}$ lands. To see where another vector ends up, take the x-coordinate of the vector and multiply by the first column and add it to the y-coordinate of the vector multiplied by the second column:

$\begin{bmatrix} a & b \\ c & d\end{bmatrix} \begin{bmatrix} x \\ y \end{bmatrix} = x \begin{bmatrix} a \\ c \end{bmatrix} + y \begin{bmatrix} b \\ d \end{bmatrix}$

The right hand side of the equation is where all the intuition for a matrix is.

Matrices gives us a way to compactly describe linear transformations. Every time you see a matrix you can think of it as a linear transformation. Matrix-vector multiplication is just way to compute what that transformation does to a given vector.

## Matrix multiplication as composition

Matrix multiplication is the composition of linear transformations.

Matrix on the right is applied first then the matrix on the left, which stems from function notation, e.g. for $f(g(x))$, we apply $g(x)$ and then $f(x)$.

For example:

$\begin{bmatrix} 0 & 2 \\ 1 & 0 \end{bmatrix} \begin{bmatrix} 1 & -2 \\ 1 & 0 \end{bmatrix}$

Think of matrix multiplication using the column view:

$\begin{bmatrix} 0 & 2 \\ 1 & 0\end{bmatrix} \begin{bmatrix} 1 \\ 1 \end{bmatrix} = 1 \begin{bmatrix} 0 \\ 1 \end{bmatrix} + 1 \begin{bmatrix} 2 \\ 0 \end{bmatrix} = \begin{bmatrix} 2 \\ 1 \end{bmatrix}$

$\begin{bmatrix} 0 & 2 \\ 1 & 0\end{bmatrix} \begin{bmatrix} -2 \\ 0 \end{bmatrix} = -2 \begin{bmatrix} 0 \\ 1 \end{bmatrix} + 0 \begin{bmatrix} 2 \\ 0 \end{bmatrix} = \begin{bmatrix} 0 \\ -2 \end{bmatrix} $

We see that order of matrix multiplication matters, because the order of transformations matters. Also, (AB)C = A(BC), which is trivial by thinking of matrices as transformations. This is an example how a deeper understanding can illuminate more than symbolic manipulations. Figuring out the "right" way to think about a problem or mathematical object.

## The determinant

It's helpful to know how much a linear transformation has scaled the space. Think of the unit rectangle stretching and shrinking. What's the area of that rectangle after the transformation? It applies to any area in the space, because any area can be approximated by tiny rectangles.

The scaling factor for any area in the space is the absolute value of the determinant. The sign of the determinant indicates flipping the area (inverting the orientation of space, i.e. flipping whether $\hat{i}$ is to the left or to the right $\hat{j}$).

In 3D, the absolute value of the determinant is the scaling factor any volume in the space. And the sign is again an inversion of orientation. If you use your index finger for $\hat{i}$, your middle finger for $\hat{j}$ and your thumb for $\hat{k}$ on your right hand to describe the orientation of the original space, can you still use your right hand to do it after the transformation or do you have to switch to using your left hand?

If $det(\textbf{A}) = 0$, then the transformation squishes space into a lower dimension.

## Inverse matrices, column space and null space

$\textbf{A} \textbf{x} = \textbf{v}$ means we're looking for a vector $\textbf{x}$, which after the linear transformation $\textbf{A}$ lands on the vector $\textbf{v}$.

Suppose $det(\textbf{A}) \ne 0$, then space does not get squished into a lower dimension. In this case, there will always be one and only vector. Following the known transformation in reverse from $\textbf{v}$ (the known quantity) gets you the vector $\textbf{x}$ (the unknown). The transformation in reverse is $\textbf{A}^{-1}$. There still could be a solution even if $\textbf{A}^{-1}$ doesn't exist, but the solution has to live in the lower dimension.

The **rank** is the number of dimensions in the output of a transformation, or more precisely in the column space. The rank helps distinguish a transformation that, for example, maps a 3D vector to a 2D one from a 3D vector to a 1D one even though in both cases the matrix associated with the transformation will have a determinant of 0. The matrix is **full rank** when the rank equals the number of columns in the matrix.

The **column space** is the span of the columns of the matrix.

The **null space** or the **kernel** is the set of all the vectors that get squished to the origin after a transformation. When $\textbf{v}$ gets squished to the origin, the null space gives you the set of solutions to your equation.

## Dot products and duality

The dot product of $\textbf{v} \cdot \textbf{w}$ is the projection of $\textbf{w}$ onto $\textbf{v}$ scaled by the magnitude of $\textbf{v}$. When $\textbf{w}$ is pointing in the opposite direction of $\textbf{v}$, then the dot product will be negative. When generally pointing in the same direction, their dot product is positive. When generally pointing in opposite directions, their dot product is negative. When perpendicular, the dot product is 0. Order doesn't matter.

There is a duality between 1x2 matrices (linear transformation that takes a vector to a number) and 2D vectors (the vectors themselves). A vector can be thought of as a conceptual shorthand for a certain type of linear transformation.

## Cross products

The cross product $\textbf{v} \times \textbf{w}$ takes two vectors in 3D space as input and returns a vector that is perpendicular to both of the input vectors.

The magnitude of the output vector is the area of the parallelogram that the input vectors span out if $\textbf{v}$ is on the right of $\textbf{w}$ and the negative of that area otherwise. Notice that the order of the input vectors to the cross product matters. This area can be computed as the determinant of the matrix where the first column is $\textbf{v}$ and the second column is $\textbf{w}$.

The direction of the output vector is perpendicular to the parallelogram and follows the "right-hand rule". The right-hand rule says to put the fore finger of your right hand in the direction of $\textbf{v}$ and stick out your middle finger in the direction of $\textbf{w}$. The direction that your thumb is pointing is the direction of the output vector.

The cross product is computed as the determinant of a matrix, where the second column is $\textbf{v}$, the third column is $\textbf{w}$ and the first column (strangely) is a vector formed from the basis vectors $\hat{i}$, $\hat{j}$ and $\hat{k}$. What does it mean to have an entry of a matrix be a vector? This is taught as a notational trick. In calculating the determinant, you'll get a linear combination of those basis vectors with scalar coefficients that are a function of the entries of $\textbf{v}$ and $\textbf{w}$.

## Change of basis

$\hat{i}$ and $\hat{j}$ encodes the implicit assumptions we make about a coordinate system: the positive direction along the x-axis, the positive direction along the y-axis and the units of distance. Any system to translate between vectors and sets of numbers is a **coordinate system**.

How do you translate between coordinate systems? Use the matrix whose columns represent the alternate basis vectors to translate from the alternate vector to the vector in our coordinate system.

Whenever you see $\textbf{A}^{-1} \textbf{M} \textbf{A}$, think (change of basis back to the alternate coordinate system) (our transformation) (change of basis to our coordinate system). The whole expression gives the $\textbf{M}$ transformation but in the alternate coordinate system. It takes a vector in the alternate coordinate system, translate it to a vector in our coordinate system, applies a transformation expressed in our coordinate system and maps it back to a vector expressed in the alternate coordinate system.

## Eigenvectors and eigenvalues

Consider a linear transformation and what happens to an arbitrary vector under that transformation. Most vectors will get knocked off of their span.

The eigenvectors of a transformation are those vectors that stay in their original span after the transformation. In other words, the transformations acts on those vectors like a scalar would. The eigenvalue is the factor by which the eigenvector is stretched (or squished or flipped) under the transformation.

For a rotation, the eigenvector gives the axis of rotation and the eigenvalue is 1 since rotations don't stretch or shrink anything. Looking at the eigenvectors of a transformations gives you a simpler way to understand what the transformation does than figuring out what happens to the basis vectors under the transformation.

Every real symmetric matrix (a real-valued matrix where the matrix is equal to its transpose) can be decomposed into $\textbf{Q}^{-1} \Lambda \textbf{Q}$ where each column of $\textbf{Q}$ is an eigenvector, the eigenvectors are orthogonal, and the diagonals of $\Lambda$ are the corresponding eigenvalues. In this case, we can interpret the original transformation as scaling the space by $\Lambda_{i,i}$ in the direction of the $i$th column of $\textbf{Q}$, which can be a more succint summary of the transformation then looking at the columns of the original transformation.

Some transformations don't have eigenvectors.

A diagonal matrix means that all basis vectors are eigenvectors and the diagonal entries are the eigenvalues.

What we can do is change to a basis where the basis vectors are eigenvectors and then our transformation in the new coordinate system will become a diagonal matrix which is easier to work with. E.g., compute the 100th power of a matrix by first changing to an eigenbasis, computing the 100th power in that coordinate system and then changing the basis back (but not all matrices have a eigenbasis).

## Sources

* https://www.3blue1brown.com/topics/linear-algebra