# Random variables

A **random variable** is a mapping from every element in the sample space, i.e., every realization or outcome, to a real number.

Technically, a random variable is **measurable mapping**, i.e., {w : X(w) <= x} is in the sigma algebra for every x.

Let X be a random variable and A be a subset of the real line. Define X^{-1}(A) as the set of all outcomes w in the sample space set that X(w) is in A. Define P(X in A) = P(X^{-1}(A)) = P({w in S : X(w) in A}). Define P(X = x) = P(X^{-1}(x)) = P(w in S : X(w) = x). We have to clarify these definitions, because we've only defined a probability distribution, or probability measure, when the input is an event. Informally, we think of a random variable as a random number, but formally it's a function defined on a sample space.

The **cumulative distribution function** for a random variable X is a function $F_{X}(x)$ from $\mathbb{R}$ to the unit interval where $F_{X}(x) = P(X \lt x)$. The CDF completely defines the probability distribution of a random variable. The CDF is defined for both discrete and continuous random variables.

A random variable X is **discrete** if it maps to countably many values. For discrete random variables, we define the **probability mass function** $f_{X}(x) = P(X = x)$.

A random variable X is **continuous** if its probability density function exist. A **probability density function** is a function f where:
* f(x) >= 0 for all x
* if you integrate the function from negative infinity to infinity then you get 1
* for every a <= b, then P(a < X < b) = the integral of the function from a to b

Note that if a random variable X is continuous then P(X = x) = 0 for every x. Also, a PDF can be bigger than 1. It can even be unbounded as long as it still integrates to 1 over the entire real line.

If X is a random variable with CDF F, then the **inverse CDF**, or **quantile function** is $F^{-1}(q) = \inf \{x : F > q\}$ for $q \in [0, 1]$. $F^{-1}(1/2)$ is the median.

Given a pair of random variables X and Y, we define the **bivariate cumulative distribution function** as $F_{X, Y} = P(X \lt x, Y \lt y)$.

Given a pair of discrete random variables X and Y, the **joint mass function** f(x, y) = P(X = x and Y = y). Given a pair of continuous random variables, we call f(x, y) a **bivariate probability density function** if:
* f(x, y) >= 0 for all x, y
* the double integral of f(x, y) from negative infinity to infinity is 1
* for any set $A \in \mathbb{R} \times \mathbb{R}$, P(X, Y \in A) = \int \int_A f(x, y) dx dy$

Some important discrete distributions:
* Point mass distribution
* Discrete uniform distribution
* Bernoulli distribution
* Binomial distribution
* Geometric distribution
	* If X is the number of flips needed until the first head when flipping a coin, then X follows a geometric distribution.
	* If X is the number of flips needed until r heads when flipping a coin, then X follows a negative binomial distribution.
* Poisson distribution
	* If X is the "number of events occurring in a fixed interval of time or space", then X follows a Poisson distribution if "these events occur with a known constant mean rate and independently of the time since the last event"
	* "The Poisson distribution is also the limit of a binomial distribution, for which the probability of success for each trial equals $lambda$ divided by the number of trials, as the number of trials approaches infinity"
	* Why do you need the rare events assumption? You need the assumption "Two events cannot occur at exactly the same instant; instead, at each very small sub-interval, either exactly one event occurs, or no event occurs." Note that "The rate of an event is related to the probability of an event occurring in some small subinterval (of time, space or otherwise). In the case of the Poisson distribution, one assumes that there exists a small enough subinterval for which the probability of an event occurring twice is 'negligible'."

Some important continuous distributions:
* Uniform distribution
* Normal distribution
* Gamma distribution
	* A 2 parameter family of continuous distributions that include the Exponential distribution and the chi-square distribution as special cases
* Exponential distribution
	* Like a geometric distribution, but continuous random variables. It describes "the time for a continuous process to change state."
	* Like the Poisson distribution, but it models waiting time between events instead of number of events.
	* The exponential distribution is just a Gamma(1, beta) distribution
* Beta distribution
	* A 2 parameter family of continuous distributions defined on the unit interval
* t-distribution
	* Take n samples from a Normal distribution. Then the ((sample mean - true mean) / ((Bessel corrected sample variance) * sqrt(n))) follows a t-distribution
	* "The t distribution is similar to a Normal but it has thicker tails."
	* The Normal distribution is a special case of the t-distribution when v = infinity 
	* The Cauchy distribution is a special case of the t-distribution when v = 1
	* "The t-distribution is symmetric and bell-shaped, like the normal distribution. However, the t-distribution has heavier tails, meaning that it is more prone to producing values that fall far from its mean. This makes it useful for understanding the statistical behavior of certain types of ratios of random quantities, in which variation in the denominator is amplified and may produce outlying values when the denominator of the ratio falls close to zero."
* Cauchy distribution
	* "It is also the distribution of the ratio of two independent normally distributed random variables with mean zero."

## Skipped

* Transformations of Random Variables
* Transformations of Several Random Variables

## Sources

* Chapter 2, "Probability", All of statistics, Wasserman
