# Anatomy of an RL algorithm

An RL algorithm can be divided into 3 parts:

* Generate samples (i.e. run the policy)
* Fit a model / estimate the return
* Improve the policy

For example, for policy gradients:

* Sample a trajectory by running the policy
* Estimate the return by calculating the sum of remaining rewards over time steps of that trajectory
* Improve the policy by taking a gradient ascent step

Or for actor-critic methods:

* Sample a trajectory by running the policy
* Estimate the return by fitting a model to estimate the sum of remaining rewards over time steps of that trajectory ($Q^{\pi}$) or relatedly by fitting a model of $A^{\pi}$ or $V^{\pi}$.
* Improve the policy by taking a gradient ascent step (plugging in the estimated return into the gradient).

## Sources

* [Introduction to Reinforcement learning, Lecture 3, Sergey Levine](http://rll.berkeley.edu/deeprlcourse/f17docs/lecture_3_rl_intro.pdf)
* [Policy gradients, Lecture 4, Sergey Levine](http://rll.berkeley.edu/deeprlcourse/f17docs/lecture_4_policy_gradient.pdf)