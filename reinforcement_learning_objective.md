# Reinforcement learning objective

Suppose we have some joint distribution $p_{\theta} \left(s_1, a_1, \dots, s_T, a_T \right)$ over all states and actions up to the last time step $T$ parameterized by $\theta$.

We define the reinforcement learning objective as:

$arg \max_{\theta} \mathbb{E}_{\left( s_1, a_1, \dots, s_T, a_T \right) \sim p_{\theta} (s_1, a_1, \dots, s_T, a_T)} \left[ \sum_{t=1}^T R \left[s_t, a_t \right]  \right]$

where $R$ is a reward function and the expectation is over the distribution of trajectories.

We can approximate this expectation in the objective by sampling trajectories. If we sample $N$ trajectories $\{ \{s_t, a_t\}_{t=1}^T \}_{i=1}^N$, then we have our approximation of the objective as:

$arg \max_{\theta} \frac{1}{N} \sum_{i=1}^N \sum_{t=1}^T R \left[s_t, a_t \right]$

Note that the dependency on $\theta$ is still there, but hidden in the sampling procedure.

How do we sample trajectories?

We factorize the distribution over trajectories into a product of parts that depend on the initial state and the policy function $\pi\_{\theta}$ and transition distribution at each time step:

$p_{\theta} \left( s_1, a_1, \dots, s_T, a_T \right) = p\left(s_1\right) \prod_{t=1}^T \left[ \pi_{\theta} \left(a_t \right | s_t) p\left(s_{t+1} | s_t, a_t \right) \right]$

This factorization implies that we can sample a trajectory $\{s_t, a_t\}_{t=1}^T$ as follows:

* Draw $s_1 \sim p\left(s_1\right)$ [Draw an initial state]
* Draw $a_1 \sim \pi_{\theta} \left(a_1 \right | s_1)$ [Run the policy to get an action]
* Draw $s_2 \sim p\left(s_2 | s_1, a_1 \right)$ [Take the action in the environment]
* Draw $a_2 \sim \pi_{\theta} \left(a_2 \right | s_2)$
* Draw $s_3 \sim p\left(s_3 | s_2, a_2 \right)$
* $\dots$
* Draw $s_T \sim p\left(s_T | s_{T-1}, a_{T-1}\right)$
* Draw $a_T \sim \pi_{\theta} \left(a_T \right | s_T)$

## Sources

* [Introduction to Reinforcement learning, Lecture 3, Sergey Levine](http://rll.berkeley.edu/deeprlcourse/f17docs/lecture_3_rl_intro.pdf)