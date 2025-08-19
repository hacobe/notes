# C

## Preliminaries

Save this program as `main.c`:

```C
#include <stdio.h>

int main(void) {
	printf("Hello, world!\n");
	return 0;
}
```

Compile it:

```bash
gcc main.c
```

Execute it:

```bash
./a.out
```

We can also step through the program if we compile with the `-g` flag:

```bash
gcc -g main.c
```

And then run LLDB:

```bash
lldb ./a.out
(lldb) b main
(lldb) r
(lldb) n
(lldb) n
```

## Variables

A variable is the human-readable name for a value stored at some address in memory.

```C
#include <stdio.h>

int main(void) {

	// Character (1 byte).
	char a = 'a';
	printf("Number of bytes for char: %zu\n", sizeof(a));
	
	// Signed integer (4 bytes).
	int b = 1;
	printf("Number of bytes for int: %zu\n", sizeof(b));

	// IEEE 754 single precision floating point (4 bytes).
	float c = 2.3;
	printf("Number of bytes for float: %zu\n", sizeof(c));

	// IEEE 754 double precision floating point (8 bytes).
	double d = 4.5;
	printf("Number of bytes for double: %zu\n", sizeof(d));

	return 0;
}
```

## Pointers

A pointer is a variable that stores a memory address. We can dereference a pointer to get its value.

```C
#include <stdio.h>

int main(void) {

	int a = 1;
	// also valid: int *p = &a;
	// note that for `int* p, q;` q will be of type int, not a pointer to an int. 
	int* p = &a;

	// a = 1, p = 0x16ef3f048, *p = 1
	printf("a = %d, p = %p, *p = %d\n", a, p, *p);

	return 0;
}
```

The void pointer is a generic pointer type. It expects an address, but an address
pointing to data of any type. For void* var, you can cast to a particular type, e.g., (int*)var.

```C
#include <stdio.h>

int main(void) {

	int a = 1;
	void* p = &a;

	// a = 1, p = 0x16d18b048, *p = 1
	printf("a = %d, p = %p, *p = %d\n", a, p, *(int*)p);

	return 0;
}
```

## Functions

When we pass a variable to a function, it makes a copy:

```C
#include <stdio.h>

int increment(int x) {
	x++;
	return x;
}

int main(void) {
	int x = 0;
	int y = increment(x);
	// x = 0, y = 1
	printf("x=%d, y=%d\n", x, y);
	return 0;
}
```

To have the function modify the value of a parameter, we need to have it copy the address, not the value (i.e., "pass-by-reference" as opposed to "pass-by-value"):

```C
#include <stdio.h>

void increment(int* p) {
	// also works: *p += 1
	// *p++ is different: *(p++);
	(*p)++;
}

int main(void) {
	int x = 0;
	increment(&x);
	// x = 1
	printf("x=%d\n", x);
	return 0;
}
```

## Arrays

An example of an array:

```C
#include <stdio.h>

int main(void) {
	int a[4] = {0, 2, 4, 6};
	// 0
	// 2
	// 4
	// 6
    for (int i = 0; i < sizeof(a) / sizeof(int); i++) {
        printf("%d\n", a[i]);
    }
}
```

The same but using pointer arithmetic instead of the index notation:

```C
#include <stdio.h>

int main(void) {
	int a[4] = {0, 2, 4, 6};
    for (int i = 0; i < sizeof(a) / sizeof(int); i++) {
    	printf("%d\n", *(a + i));
    }
}
```

We can pass it to a function by passing a pointer to the first element of the array:

```C
#include <stdio.h>

// same as: void times2(int a[], int len) ...
// same as: void times2(int a[4], int len) ...
void times2(int* a, int len) {
    for (int i = 0; i < len; i++) {
        printf("%d\n", a[i] * 2);
    }
}

int main(void) {
	int a[4] = {0, 2, 4, 6};
	// a is a pointer to the first element of the array.
    times2(a, 4);
    // a = 0x16f25f030, &a[0] = 0x16f25f030
    printf("a = %p, &a[0] = %p\n", a, &a[0]);
}
```

For a multidimensional array, we need to pass at least the non-batch dimensions:

```C
#include <stdio.h>

// same as: void times2(int a[][3], int len) ...
void times2(int a[2][3], int nrow, int ncol) {
    for (int r = 0; r < nrow; r++) {
    	for (int c = 0; c < ncol; c++) {
        	printf("%d\n", a[r][c] * 2);
		}
		printf("\n");
    }
}

int main(void) {
	int a[2][3] = {{1, 2, 3}, {4, 5, 6}};
    times2(a, 2, 3);
}
```

## Strings

An example of a string:

```C
#include <stdio.h>

int main(void) {
	// immutable string
	// (null-terminated)
	char* a = "Hello, world!";

	// mutable string
	// (null-terminated)
	char b[] = "Hello, world!";

	printf("a = <%s>, b = <%s>\n", a, b);
}
```

Examples of a few string functions:

```C
#include <stdio.h>
#include <string.h>

int main(void) {
	char* a = "Hello, world!";
	char b[100];
	strcpy(b, a);

	// b = <Hello, world!>, strlen(b) = 13
	printf("b = <%s>, strlen(b) = %zu\n", b, strlen(b));
}
```

## Structs

An example of a struct:

```C
#include <stdio.h>

struct my_structure {
	int a;
	char* b;
};

void times2(struct my_structure* s) {
	printf("%d, %s\n", 2 * s->a, s->b);
}

int main(void) {
	struct my_structure s = {.a = 1, .b = "bar"};
	printf("%d, %s\n", s.a, s.b);
	times2(&s);
}
```

A struct and functions that take a pointer to the struct are a bit like classes.

## Memory allocation

An example of memory allocation:

```C
#include <stdlib.h>
#include <stdio.h>

int main(void) {
    int *p = malloc(sizeof(int) * 10);

    for (int i = 0; i < 10; i++) {
        p[i] = i * 5;
    }

    for (int i = 0; i < 10; i++) {
        printf("%d\n", p[i]);
    }

    free(p);
}
```

The heap is whatever pool of memory `malloc` requests from the operating system for allocations. We use it to allocate memory when the amount of memory to allocate is determined at runtime or relatedly when  data structures grow or shrink at runtime or for larger data structures that exceed stack memory or for data that persists beyond the scope of a function.

## Sources

* https://beej.us/guide/bgc/html/split/
* "Introduction to C", https://csprimer.com/courses/systems/
