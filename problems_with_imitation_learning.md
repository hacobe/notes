# Problems with imitation learning

Can you just collect observations and actions from an expert source and then train a policy that predicts actions from observations using supervised learning?

In theory, no, because of distributional shift. When you go to test the policy that you’ve trained, i.e. to run the policy on a new set of observations, then every once in a while the policy will make a small mistake deviating from the expert source. Over time, these mistakes will compound until the distribution you’re testing on is very different from the distribution you trained on. The fact that the observation at a time step depends on previous actions (the data is not i.i.d.) and that the distribution evolves over time underlies this problem.

## Sources

* [Supervised Learning of Behaviors, Lecture 2, Sergey Levine](https://rll.berkeley.edu/deeprlcourse/f17docs/lecture_2_behavior_cloning.pdf)
