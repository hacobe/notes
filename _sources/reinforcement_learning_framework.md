# Reinforcement learning framework

The reinforcement learning framework expands the supervised learning framework to capture an agent interacting with an environment over time. This enables models that can change how the data are sampled based on their predictions. It also enables models that can receive delayed feedback in the form of rewards for actions taken at previous time steps.

In particular, in the reinforcement learning framework, at each time step $t$:

* The agent executes an action and receives an observation and scalar reward.
* The environment receives the action from the agent, emits the next observation and emits the next scalar reward.
* The time step increments.


The goal of the agent is to choose the actions that maximize the cumulative expected reward over all time steps.

## Sources

* [Introduction to Reinforcement Learning, David Silver](http://www0.cs.ucl.ac.uk/staff/d.silver/web/Teaching_files/intro_RL.pdf)
* [Supervised Learning of Behaviors, Lecture 2, Sergey Levine](http://rll.berkeley.edu/deeprlcourse/f17docs/lecture_2_behavior_cloning.pdf)
