https://pytorch.org/tutorials/beginner/basics/autogradqs_tutorial.html
https://github.com/pytorch/examples/blob/master/mnist/main.py
https://pytorch.org/tutorials/beginner/blitz/cifar10_tutorial.html
https://github.com/ddbourgin/numpy-ml/blob/master/numpy_ml/neural_nets/layers/layers.py

* make sure dy is incorporated in the backward pass
* test backward pass of activations by multiplying by constant and taking the sum
* be careful about whether you're using log softmax vs softmax
* be careful about whether you're using BinaryCrossEntropy vs NLLLoss
* sometimes what's online is after canceling out certain terms and isn't strictly comparable to what i'm doing
* sometimes breaking up the computation into layers actually makes things more complicated and it'd be easier to just do it one function like softmax_regression.py, logistic_regression.py, linear_regression.py