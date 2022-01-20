# Automatic differentiation

**Automatic differentiation** is a technique for computing the gradient of a function specified by a computer program.

It takes advantage of the fact that any function implemented in a computer program can be decomposed into primitive operations (or else how would the function be implemented in the first place?), which are themselves easy to differentiate and whose derivatives can then be combined to get the derivative of the original function.

For example, suppose our primitive operations are multiplying by a constant, adding a constant and exponentiating by a constant. And the function we want to differentiate is $f(x) = 2 x^3 + 7$. We can write $f(x)$ as a composition of primitive operations. Define $f_1(x) = x + 7$, $f_2(x) = 2x$, $f_3(x) = x^3$. Then $f(x) = f_1(f_2(f_3(x)))$.

We can apply the chain rule to get the derivative. Define $g(x) = f_2(f_3(x))$. The chain rule states that $\frac{\partial} {\partial x} [ f_1(g(x)) ] = f'(g(x)) g'(x)$. By the same token, $g'(x) = f_2'(f_3(x)) f_3'(x)$. Putting that together, we have $f'(x) = f_1'(f_2(f_3(x))) f_2'(f_3(x)) f_3'(x)$, which is the derivate of the original function written in terms of the derivative of primitive operations.

How do we do this more generally? First, we need a way to represent a function. Supposing that we can decompose a function into primitive operations, then we can represent a function as a **computational graph** where each node in the graph (a directed acyclic graph) is either a primitive operation or a variable. For example, the computational graph for $f(x, y, z)  = (x + y) \cdot z$ looks like:


	    *
	   / \
	  +   z
	 / \
	x   y 


An automatic differentiator takes the root of a computational graph as input and values for the variable nodes and returns the gradient of the function evaluated at those input values.

**How do we compute the gradient using the graph?** Even though we don't yet know how to calculate the partial derivative of the root node with respect to one of its grandchildren ($x$ or $y$), we first notice that it's easy to calculate the partial derivative of a node with respect to one of its children, because each parent node is a primitive operation and we know how to calculate derivatives for primitive operations by applying one of a few formulas. For example, relabel the computational graph above with $a = x + y$ and $b = az$:

        b
        *
	   / \
	  a   z
	  +   
	 / \
	x   y 

The partial derviative of the $b$ node with respect to its child node $a$ is just $\frac{\partial}{\partial a} b = \frac{\partial}{\partial a} a \cdot z = a \frac{\partial{z}}{\partial{a}} + z \frac{\partial{a}}{\partial{a}} = z$ according to the product rule of calculus.

We can label each edge with the partial derivative of the parent/destination node with respect to its child/source node. Now, how do we use that information to get the partial derivatives of the root with respect to each of the leaf/variable nodes in the graph? For a given leaf node, it turns out that the sum over all the paths from that leaf to the root of the product of the edges for each path gives you the partial derivative of the root node with respect to the leaf node.

That procedure is just a visual way of describing the multivariate chain rule. Suppose we have a function $f(u_1, u_2, \cdots, u_n)$ where the input variables depend on some other variable $x$ ($f$ should be thought of as the root node in the graph, $u_i$ as intermediate nodes and $x$ as a leaf node), then $\frac{\partial f}{\partial x} = \sum_{i=1}^n \frac{\partial f}{\partial u_i} \frac{\partial u_i}{\partial x}$.

**Forward and reverse mode accumulation**: The way that we traverse the graph to compute these partial derivatives can dramatically alter the efficiency of the computation. Consider the following graph:

         y
         |
         uk
         |
         .
         .
         .
         |
         u1
         +
      / | | \
     x1 ... xp

If we want to calculate the gradient of $y$ and we start from the leaf nodes and move up, then we first calculate $\frac{\partial y}{\partial x_1} = \frac{\partial u_1}{\partial x_1} \frac{\partial u_2}{\partial u_1} \dots \frac{\partial u_k}{\partial u_{k-1}} \frac{\partial y}{\partial u_k}$. We then sweep through the graph again to calculate $\frac{\partial y}{\partial x_2} = \frac{\partial u_1}{\partial x_2} \frac{\partial u_2}{\partial u_1} \dots \frac{\partial u_k}{\partial u_{k-1}} \frac{\partial y}{\partial u_k}$. And again for $\frac{\partial y}{\partial x_3}$ and so on. Each time repeating the computation $\frac{\partial u_2}{\partial u_1} \dots \frac{\partial u_k}{\partial u_{k-1}} \frac{\partial y}{\partial u_k}$. This is forward mode accumulation and it requires $k \cdot p$ multiplies to get the gradient.

If we instead start from the top of the graph and move downwards caching the results as we go, then we first calculate $\frac{\partial y}{\partial u_k}$, then $\frac{\partial y}{\partial u_{k-1}}$ as $\frac{\partial y}{\partial u_k} \cdot \frac{\partial u_k}{\partial u_{k-1}}$ using the cached value for the first term and so on down the graph. This is reverse mode accumulation and it only requires $k + p$ multiplies to get the gradient. In the case of gradient descent on the cost function of a neural network with millions of parameters, automatic differentiation with reverse mode accumulation (also called **backpropagation**) makes optimization feasible. 

## Sources

* https://colah.github.io/posts/2015-08-Backprop/
* https://www.offconvex.org/2016/12/20/backprop/
* https://en.wikipedia.org/wiki/Automatic_differentiation
* https://arxiv.org/pdf/1811.05031.pdf