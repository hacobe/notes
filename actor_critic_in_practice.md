# Actor-critic methods in practice

*Separate or unified actor-critic?*

Should you (A) use separate networks for the actor and the critic or (B) share the weights of the actor and critic networks?

(B) might be good if the states are very high dimensional, but it's not as stable, because then you have two very different gradients flowing through the weights, which means you might need more experimentation with the network initialization and the learning rates.

Levine suggests starting with (A) if you're developing algorithms on a fairly fast simulator (e.g. MuJoCo).

*Bigger batches*

A batch size of 1 for the online actor-critic algorithm isn't very stable. You could collect more sample trajectories, form a batch and then update the networks less frequently. You could also collect samples in parallel.

*Synchronized, parallel actor-critic*

You can also parallelize the actor-critic algorithm and have, for example, 4 separate threads that each take one step with a given policy network in the environment. You can then form a batch of the 4 steps and take a gradient step with this batch (this step is the synchronized step).

## Sources

* [Actor-critic algorithms, Lecture 5, Sergey Levine](http://rll.berkeley.edu/deeprlcourse/f17docs/lecture_5_actor_critic_pdf.pdf)
