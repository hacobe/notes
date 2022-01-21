# Naive bayes

Naive bayes is a multi-class classifier that makes the assumption of independence of the probability of of the features given the class.

We want the MAP estimate of the class, i.e., what's the class with maximum posterior probability given the $p$ features?

For one point $\textbf{x} \in \mathbb{R}^p$ (the transpose of a row vector in the design matrix that you want to predict for) that we want to classify, i.e. find $y \in \mathbb{N}$:

$arg \max_y P(y \mid \textbf{x})$

Apply Bayes rule:

$= arg \max_y \frac{P(\textbf{x} \mid y) P(y)}{P(\textbf{x})}$

Throw out the numerator because it does not depend on $y$:

$= arg \max_y P(\textbf{x} \mid y) P(y)$

Write out the individual components of $\textbf{x}$:

$= arg \max_y P(x_1, \cdots, x_p \mid y) P(y)$

Make the **naive** assumption of independence of features conditioning on the class:

$= arg \max_y \left[P(y) \prod_{k=1}^p P(x_k \mid y) \right]$