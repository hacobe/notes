# Post-hoc calibration

Post-hoc calibration methods attempt to improve calibration by adjusting the predicted probabilities of a model after training.

Suppose we train a model on a binary classification task. Call this model the "base model". We predict the probability of a positive label for each example on a validation dataset using this base model. **Platt scaling** consists of running a logistic regression on the validation dataset, where the only feature is the predicted probability from the base model and the label is the original label or a modified "soft" label that attempts to introduce additional regularization (https://en.wikipedia.org/wiki/Platt_scaling). Call this second model the "calibrator". We then use the predicted probabilities from the calibrator rather than the predicted probabilities from the base model.

A variant of Platt scaling is **temperature scaling**, where we divide the logits from a classifier by a scalar, positive temperature parameter before passing them through the softmax. Larger values of the temperature make the probability distribution look more like a uniform distribution, while smaller values make the probability distribution sharper. [GPS+17](https://arxiv.org/pdf/1706.04599.pdf) popularized temperature scaling for neural networks. [OFR+19](https://arxiv.org/pdf/1906.02530.pdf) found that "temperature scaling leads to well-calibrated uncertainty on the i.i.d. test set and small values of shift, but is significantly outperformed by methods that take epistemic uncertainty into account as the shift increases." A nice feature of temperature scaling is that it does not change the order of the class probabilities, so it only affects calibration and not accuracy.

Other post-hoc calibration methods include histogram binning and isotonic regression.