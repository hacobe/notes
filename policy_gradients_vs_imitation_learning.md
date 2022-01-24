# Policy gradients vs. imitation learning

The REINFORCE algorithm is the same algorithm as imitation learning via maximum likehood if we drop the sum of rewards term in the gradient and sample the trajectories from running an expert policy function instead of $\pi_{\theta}$.

From the "Deep Reinforcement Learning: Pong from Pixels" blog post:

* "Policy gradients is exactly the same as supervised learning with two minor differences: 1) We don’t have the correct labels $y_i$ so as a "fake label" we substitute the action we happened to sample from the policy when it saw $x_i$, and 2) We modulate the loss for each example multiplicatively based on the eventual outcome, since we want to increase the log probability for actions that worked and decrease it for those that didn't."
* "So reinforcement learning is exactly like supervised learning, but on a continuously changing dataset (the episodes), scaled by the advantage, and we only want to do one (or very few) updates based on each sampled dataset."

## Sources

* [Policy gradients, Lecture 4, Sergey Levine](http://rll.berkeley.edu/deeprlcourse/f17docs/lecture_4_policy_gradient.pdf)
* [Deep Reinforcement Learning: Pong from Pixels, Andrej Karpathy](http://karpathy.github.io/2016/05/31/rl/)