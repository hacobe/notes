# Typology of RL algorithms

*Types of algorithms:*

* Policy gradients: directly differentiate the sum of rewards
* Value-based: model the value function and don't have an explicit policy
* Actor-critic: estimate the value function and use it to improve the policy

*On policy vs off policy:*

On policy if "each time the policy is changed, even a little bit, we need to generate new samples", e.g., one gradient step can change the policy and require generating new samples. Off policy: "able to improve the policy without generating new samples from that policy", i.e., we can use historical data to make the current policy better.

*Trade-offs:*

* Sample efficiency: how many samples do we need to get a good policy?
* Wall clock time: Sometimes sample inefficient algorithms are more parallelizable so may be faster than efficient, because you can distribute their computation.
* Stability and ease of use: Does it converge? If it converges, to what? does it converge every time?
* Is it easier to represent the policy or the value function?

*Assumptions:*

* Stochastic or deterministic?
* Continuous or discrete action space?
* Episodic or infinite horizon?
* Full observability?

## Sources

* [Actor-critic algorithms, Lecture 3, Sergey Levine](http://rll.berkeley.edu/deeprlcourse/f17docs/lecture_3_rl_intro.pdf)
