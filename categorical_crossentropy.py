"""Implementation of categorical cross-entropy.

Sources:
* https://pytorch.org/docs/stable/generated/torch.nn.CrossEntropyLoss.html
* https://discuss.pytorch.org/t/categorical-cross-entropy-loss-function-equivalent-in-pytorch/85165/3
* https://github.com/scikit-learn/scikit-learn/blob/main/sklearn/metrics/tests/test_classification.py#L2466
"""
import numpy as np
import scipy.special
import sklearn.metrics
import torch


def categorical_crossentropy_from_probs(y_true, y_prob, eps=1e-12):
    # y_true: (n, k) one hot encoding
    # y_prob: (n, k)
	assert eps > 0
	y_prob_clipped = np.clip(y_prob, eps, 1. - eps)
	return -np.mean(np.sum(y_true * np.log(y_prob_clipped), axis=1))


def categorical_crossentropy_from_logits(y_true, y_logits):
    # y_true: (n, k) one hot encoding
    # y_logit: (n, k)
	y_logprob = scipy.special.log_softmax(y_logits, axis=1)
	return -np.mean(np.sum(y_true * y_logprob, axis=1))


def categorical_crossentropy_from_logprobs(y_true, y_logprobs):
    # y_true: (n, k) one hot encoding
    # y_logprobs: (n, k)
	return -np.mean(np.sum(y_true * y_logprobs, axis=1))


def categorical_crossentropy_from_dense_targets_and_probs(y_true_dense, y_prob):
	# y_true: (n, ) dense encoding
	# y_prob: (n, k)

	# we can avoid converting to one hot
	# also, no sum is needed here
	return -np.mean(np.log(y_prob[np.arange(len(y_prob)), y_true_dense]))



if __name__ == "__main__":
	########
	# torch
	########

	np.random.seed(0)
	n = 3
	k = 5
	logits = np.random.randn(n, k)
	probs = scipy.special.softmax(logits, axis=1)
	logprobs = scipy.special.log_softmax(logits, axis=1)
	targets = np.random.randint(0, 5, size=n)
	logits_tensor = torch.FloatTensor(logits)
	targets_tensor = torch.LongTensor(targets)
	logprobs_tensor = torch.FloatTensor(logprobs)

	with torch.no_grad():
		expected_cel = torch.nn.CrossEntropyLoss()(
			logits_tensor, targets_tensor).tolist()
		expected_nll = torch.nn.NLLLoss()(
			logprobs_tensor, targets_tensor).tolist()

	targets_one_hot = np.zeros((n, k))
	targets_one_hot[np.arange(n), targets] = 1
	actual_from_probs = categorical_crossentropy_from_probs(targets_one_hot, probs)
	actual_from_logits = categorical_crossentropy_from_logits(targets_one_hot, logits)
	actual_from_logprobs = categorical_crossentropy_from_logits(targets_one_hot, logprobs)
	actual_from_probs_and_dense_targets = categorical_crossentropy_from_dense_targets_and_probs(
		targets, probs)

	np.testing.assert_almost_equal(actual_from_probs, expected_cel)
	np.testing.assert_almost_equal(actual_from_logits, expected_cel)
	np.testing.assert_almost_equal(actual_from_logprobs, expected_cel)
	np.testing.assert_almost_equal(
		actual_from_probs_and_dense_targets, expected_cel)
	np.testing.assert_almost_equal(expected_cel, expected_nll, decimal=6)

	##########
	# sklearn
	##########

	y_true = [0, 0, 0, 1, 1, 1]
	y_true_one_hot = np.zeros((6, 2))
	y_true_one_hot[np.arange(6), y_true] = 1
	y_prob = np.array(
		[[0.5, 0.5],
		 [0.1, 0.9],
		 [0.01, 0.99],
		 [0.9, 0.1],
		 [0.75, 0.25],
		 [0.001, 0.999]])
	actual = categorical_crossentropy_from_probs(y_true_one_hot, y_prob)
	expected = sklearn.metrics.log_loss(y_true_one_hot, y_prob)
	np.testing.assert_almost_equal(actual, expected)
	expected_manual = -1 * np.mean([
		np.log(0.5),
		np.log(0.1),
		np.log(0.01),
		np.log(0.1),
		np.log(0.25),
		np.log(0.999)])
	np.testing.assert_almost_equal(actual, expected_manual)

	#############
	# unit tests
	#############

	# basic
	y_true_one_hot = [[0, 1, 0], [1, 0, 0], [0, 0, 1]]
	y_prob = np.array([[0.2, 0.7, 0.1], [0.6, 0.2, 0.2], [0.6, 0.1, 0.3]])
	actual = categorical_crossentropy_from_probs(y_true_one_hot, y_prob)
	expected = -1 * np.mean([np.log(0.7), np.log(0.6), np.log(0.3)])
	np.testing.assert_almost_equal(actual, expected)

	# eps
	y_prob = y_prob > 0.5 # make all examples 100% confident
	actual = categorical_crossentropy_from_probs(y_true_one_hot, y_prob, eps=0.1)
	expected = -1 * np.mean([np.log(0.9), np.log(0.9), np.log(0.1)])
	np.testing.assert_almost_equal(actual, expected)


