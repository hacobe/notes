# Support vector machines

A support vector machine (SVM) is like logistic regression, but instead of maximizing the likelihood of the data, it tries to find the hyperplane that divides the positive and negative examples with as large a gap, or "margin", between them as possible.

## What are support vectors?

Support vectors are the data points closest to the hyperplane.

## What is the representation?

The representation is $g(\textbf{w}^T \textbf{x}^{(i)} + b)$ where $g(z) = \mathrm{sgn}(z)$, so it's the same representation as logistic regression except with a sign function instead of a sigmoid.

## What is the optimization objective?

For this discussion, let $\textbf{y}_i \in \{-1, 1\}$. Then we can write the "soft margin" SVM objective as:

$\min_{\textbf{w}, b} \left[\frac{1}{n} \sum_{i=1}^n \max(0, 1 - \textbf{y}_i (\textbf{w}^T \textbf{x}^{(i)} + b))\right] + \lambda \lVert \textbf{w} \rVert^2$


## Sources

* https://see.stanford.edu/materials/aimlcs229/cs229-notes3.pdf
* Goodfellow, Deep Learning
* https://www.quora.com/What-are-the-objective-functions-of-hard-margin-and-soft-margin-SVM
