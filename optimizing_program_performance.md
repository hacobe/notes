# Optimizing Program Performance

Suppose we have the following data structure for a vector in C:

```C
typedef struct {
	long len;	
	double *data;
} vec;

vec* new_vec(long len) {
	vec* result = (vec*) malloc(sizeof(vec));
	double *data = NULL;
	if (!result)
		return NULL;
	result->len = len;
	if (len > 0) {
		data = (double *)calloc(len, sizeof(double));
		if (!data) {
			free((void *) result);
			return NULL;
 		}
	}
	result->data = data;
	return result;
}

double* get_vec_start(vec* v) {
	return v->data;
}

int get_vec_element(vec* v, long index, double *dest) {
	if (index < 0 || index >= v->len)
		return 0;
	*dest = v->data[index];
	return 1;
}

long vec_length(vec* v) {
	return v->len;
}

void product(vec* v, double *dest) {
	long i;
	*dest = 1;
	for (i = 0; i < vec_length(v); i++) {
		double val;
		get_vec_element(v, i, &val);
		*dest *= val;
	}
}
```

And we want to improve the performance of the `product` function.

We measure the performance using the **Cycles Per Element (CPE)**, i.e., the additional CPU cycles required to execute the function per additional element in the input vector. We estimate the CPE by collecting a dataset of (input vector length, CPU cycles) pairs and regressing CPU cycles on vector length to estimate the slope and intercept of the least squares line. The slope is the CPE.

The `gcc` compiler allows us to chose a level of optimization. In general, the higher the level, the better the program performance, but the longer the compilation time, the larger the program size and the harder to debug. Disabling optimizations (`-O0`) yields a CPE for the `product` function of 20.18. Enabling the first level of optimization (`-O1`) yields a CPE of 11.14.

How do we improve performance over this baseline?

Our first optimization is to **move loop-invariant code in the loop outside of the loop**. In this case, we move the call to `vec_length` outside of the loop:

```C
void product1(vec* v, double *dest) {
	long i;
	long length = vec_length(v);
	*dest = 1;
	for (i = 0; i < length; i++) {
		double val;
		get_vec_element(v, i, &val);
		*dest *= val;
	}
}
```

This optimization reduces the CPE to 11.03.

The compiler does not apply this optimization automatically, because of the presence of an **optimization blocker**, i.e., an issue that prevents the compiler from guaranteeing that an optimization won't change the behavior of the program. In this case, the optimization blocker is a function call that could have **side effects**. The compiler cannot reliably rule out that `vec_length` has side effects, so it does not move the function outside of the loop.

Our second optimization is to **remove unnecessary memory references**. `product1` accumulates the value using the location designated by the pointer `dest`. This approach requires reading from memory and writing to memory on each iteration. We eliminate these memory transfers by using a local variable to accumulate the product inside the loop instead:

```C
void product2(vec* v, double *dest) {
	long i;
	long length = vec_length(v);
	double *data = get_vec_start(v);
	double acc = 1;
	for (i = 0; i < length; i++) {
		acc *= data[i];
	}
	*dest = acc;
}
```

This optimization reduces the CPE to 5.01.

The compiler does not apply this optimization automatically, because of the possiblity of **memory aliasing**, i.e., multiple variables referring to the same memory location. Consider the function calls `product1(v, get_vec_start(v) + 2)` and `product2(v, get_vec_start(v) + 2)` for the vector [2, 3, 5]. In the first function call, we have [2, 3, 1] before the loop, [2, 3, 2] after the first iteration, [2, 3, 6] after the second iteration and [2, 3, 36] after the third iteration. In the second function call, we have [2, 3, 5] before the loop, after the first iteration and after the second iteration and [2, 3, 30] after the third  iteration. This example shows that the 2 functions can produce different results, so the compiler does not transform the first function into the second.

The next change we make is to do **loop unrolling**, i.e., a program transformation that reduces the number of iterations for a loop by increasing the number of elements computed on each iteration. It can improve performance  by reducing the overhead of the loop. In this case, it does not improve performance, but it sets us up for the next optimization, which will improve performance.

```C
void product3(vec* v, double *dest)
{
	long i;
	long length = vec_length(v);
	long limit = length-1;
	double *data = get_vec_start(v);
	double acc = 1;
	for (i = 0; i < limit; i+=2) {
		acc *= data[i];
		acc *= data[i+1];
	}
	for (; i < length; i++) {
		acc *= data[i];
	}
	*dest = acc;
}
```

Why doesn't loop unrolling improve performance here? It turns out we have already hit the **latency bound**, i.e., the bound encountered when a series of operations must be performed in strict sequence, because the result of one operation is required before the next one can begin.

First, here is the assembly code for the loop in `product2`:

```assembly
.L25:  ; loop:
	vmulsd (%rdx), %xmm0, %xmm0  ; Multiply acc by data[i]
	addq $8, %rdx  ; Increment data+i
	cmpq %rax, %rdx  ; Compare to data+length
	jne .L25  ; If !=, goto loop
```

We draw the **data dependencies**, i.e., the relationship between operations that must be performed in strict sequence:

```
%xmm0       %rdx
  |           |
  v           |
 mul <-load <-|
  |           |
  |          add
  |           |
  v           v
%xmm0       %rdx
```

The critical path is the lefthand side, because the latency of multiplication is larger than the latency of addition. The critcal path has 1 multiplication, so the CPE of the program is just the latency of the multiplication operation.

Here is the assembly code for the unrolled loop in `product3`:

```assembly
.L35:  ; loop:
	vmulsd (%rax,%rdx,8), %xmm0, %xmm0  ; Multiply acc by data[i]
	vmulsd 8(%rax,%rdx,8), %xmm0, %xmm0  ; Multiply acc by data[i+1]
	addq $2, %rdx  ; Increment i by 2
	cmpq %rdx, %rbp  ; Compare to limit:i
	jg .L35  ; If >, goto loop
```

We draw the data dependencies:

```
%xmm0       %rdx
  |           |
  v           |
 mul <-load <-|
  |           |
  v           |
 mul <-load <-|
  |           |
  |          add
  |           |
  v           v
%xmm0       %rdx
```

We have cut the number of iterations in half, but we have doubled the number of multiplications on the critical path, so the CPE is the same.

To improve performance below the latency bound, we exploit the **superscaler processor**, i.e., a processor that implements instruction-level parallelism, or the simultaneous execution of a sequence of instructions in a computer program.

In particular, we apply a **reassociation transformation**, i.e., a restructuring of the computation to change the order of operations and break the sequential dependency. In particular, we change `acc *= data[i]; acc *= data[i+1];` to `acc *= (data[i] * data[i+1]);`.

```C
void product4(vec* v, double *dest)
{
	long i;
	long length = vec_length(v);
	long limit = length-1;
	double *data = get_vec_start(v);
	double acc = 1;
	for (i = 0; i < limit; i+=2) {
		acc *= (data[i] * data[i+1]);
	}
	for (; i < length; i++) {
		acc *= data[i];
	}
	*dest = acc;
}
```

We draw the data dependencies again:

```
%xmm1          %rdx
  |              |
  |    load <----|
  |     | load <-|
  |     | |      |
  |     v v      |
 mul <- mul     add
  |              |
  v              v
%xmm1          %rdx
``` 

The path on the lefthand side is the critical path. It only has 1 multiplication and we have cut the number of iterations in half.

This optimization reduces the CPE to 2.51.

Alternatively, we could use **multiple accumulators**.

```C
void product5(vec* v, double *dest)
{
	long i;
	long length = vec_length(v);
	long limit = length-1;
	double *data = get_vec_start(v);
	double acc0 = 1;
	double acc1 = 1;
	for (i = 0; i < limit; i+=2) {
		acc0 *= data[i];
		acc1 *= data[i+1];
	}
	for (; i < length; i++) {
		acc0 *= data[i];
	}
	*dest = acc0 * acc1;
}
```

We draw the data dependencies:

```
%xmm0       %xmm1       %rax
  |           |           |
  v           |           |
 mul <-load---|-----------|
  |           |           |
  |          mul <-load---|
  |           |           |
  |           |          add
  |           |           |
  v           v           v
%xmm0       %xmm1       %rax
```

The path on the lefthand side and the path in the middle are the critical paths. Each critical path has 1 multiplication, each of those multiplications is done in parallel and we have cut the number of iterations in half.

This optimization also reduces the CPE to 2.51.

Increasing the number of accumulators to 10 further reduces the CPE to 0.52.

The compiler does not make these optimizations because floating-point operations are not associative in practice due to rounding errors - changing the grouping or order of operations may produce different numerical results.

At this point, the program runs into the **throughput bound**. **Issue time** is the minimum number of cycles between two independent operations. A processor has multiple functional units to execute an operation. The **throughput** of a processor for an operation, or the number of operations per clock cycle, is the product of the capacity (how many of the operations can be issued simultaneously) and the reciprocal of the issue time.

## Sources

* "5 Optimizing Program Performance", Computer Systems: A Programmer's Perspective