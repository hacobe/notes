# Structured prediction

What makes structured prediction different from classification or regression?
* A very large output space
* The need for approximate methods to generate a prediction (e.g., beam search or ancestral sampling)
* The complexity of evaluating the quality of the output (e.g., quality may be multi-dimensional rather than just correct or incorrect)
* The mismatch between the training objective and our true, complex notion of quality
* The output can be very informative of quality