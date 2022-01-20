# Broadcasting

Broadcasting is a way of making an elementwise operation that takes 2 arrays as input work when those arrays have different shapes. It is an algorithm that attempts to create 2 arrays with the same shape based on the 2 original input arrays so that the elementwise operation can be applied. The algorithm goes as follows:

* Make the rank of A and B the same by prepending dims of size 1
* Create the output dims by iterating through the new shape. Take the greater size for each dim as long as the other one has size 1 (if not then the shapes are incompatible for broadcasting).

For both A and B:
* Initialize output to zeros in the shape given by output dims
* Iterate through all possible output indices and set the output at certain indices to the input at those indices (if output index is greater than the size of the input in that dimension then set the input index to 0 because the size of the input in that dimension must be 1)

* Now the output A and B have the same shape and we can perform an elementwise operation

For vectors and matrices, we can explain it visually as follows:

<img src="https://i.stack.imgur.com/JcKv1.png" />

## Sources

* https://mathematica.stackexchange.com/questions/99171/how-to-implement-the-general-array-broadcasting-method-from-numpy