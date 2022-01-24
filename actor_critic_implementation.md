# Actor-critic implementation

(This is just one variation)

* Build two separate models: an actor (policy network: [batch_size, state_size] => [batch_size, action_size]) and a critic (value network: [batch_size, state_size] => [batch_size, 1])
* The actor is setup as the policy network is in REINFORCE, while the critic uses MSE loss.
* Training is done online after each time step instead of every episode, so there's no need to save experiences as in REINFORCE.

Sketch of training:

	value = critic.predict(state)[0, 0]
	next_value = critic.predict(next_state)[0, 0]

	target_value = np.zeros((1, 1))
	target_value[0, 0] = reward + (discount_rate if not done else 0)*next_value

	target_advantage = np.zeros((1, action_size))
	target_advantage[0, action] = target_value - value

	critic.fit(state, target_value, epochs=1)
	actor.fit(state, target_advantage, epochs=1)

## Sources

* [rlcode, CartPole A2C](https://github.com/rlcode/reinforcement-learning/blob/master/2-cartpole/4-actor-critic/cartpole_a2c.py)

