# Linear discriminant analysis

Linear discriminant analysis (LDA) is a linear classification method. Logistic regression directly models $P(y \mid x)$. From Bayes' Rule, we get $P(y \mid x) = \frac{P(x \mid y) P(y)}{P(x)}$. Instead of modeling $P(y \mid x)$ directly, LDA models $P(x, y) = P(x \mid y)P(y)$ ($P(x)$ doesn't depend on the class). In particular, it assumes that the conditional distribution of $x$ given $y$ is a multivariate Gaussian. With a training dataset, we can estimate the mean and the covariance of the Gaussian for $y = 1$ and the mean and the covariance for $y = 0$. We set the densities equal to find the decision boundary that separates the classes. Different assumptions about the covariance matrices lead to different methods:

| *Covariance matrices* | Different across classes | Same across classes |
|-----------------------|--------------------------|---------------------|
| **Full**		        | QDA                      | Diagonal QDA        |
| **Diagonal**		    | Naive Bayes              | Diagonal LDA        |
| **Spherical**		    | Spherical QDA            | Nearest centroid    |

Note that LDA makes a distribution assumption about the features, while logistic regression makes no such assumption.

## Sources

* [Lecture 6](https://www.youtube.com/watch?v=C0u_v7vEDBY), Introduction to Machine Learning, Dmitry Kobak, Winter Term 2020/21 at the University of Tübingen
* https://www.quora.com/Does-logistic-regression-require-independent-variables-to-be-normal-distributed
* https://online.stat.psu.edu/stat508/lesson/9/9.2/9.2.9
