# Assembly

A computer contains hardware to execute a certain set of fundamental instructions (called "machine code instructions"). Assembly language is a programming language where the instructions in the language have a very close correspondence to the machine code instructions baked into the hardware. In fact, most instructions in assembly language have a one-to-one correspondence with these machine code instructions. Some "pseudo-instructions" in the language can be translated into a few instructions. An assembler is a program that converts assembly language code to machine code instructions.

Because of this close correspondence between assembly language and machine code instructions, an assembly language is specific to a particular computer architecture (or "instruction set architecture"). There are different assembly languages for different computer architectures. In contrast, you can write a program in C and compile it to machine code for any given architecture rather than having to rewrite the program in the assembly language specific to that architecture.

We focus on the MIPS computer architecture, which is an example of a Reduced Instruction Set Computer (RISC) architecture. We model the computer as having a processor and memory. The processor contains 32 registers, which are places to store data on the processor (as opposed to memory, which is "far away" from the processor). Each of the 32 registers can store a 32 bit binary number. Assembly language instructions can load data from memory to registers, perform operations using the data in the registers, store the result of operations in registers and move data from the registers back to memory.

## Registers

A register is referred to as `$i` in assembly language where `$i` in the range [0, 31] or by one of the following names:

```
$zero: Register hardwired to store 0.
$at: Register reserved for the assembler
$v0-$v1: Registers to store function return values.
$a0-$a3: Registers to store function arguments.
$t0-$t9: Registers to store temporary variables.
$s0-$s7: Register to store variables.
$gp: Register to store the global pointer.
$sp: Register to store the stack pointer.
$fp: Register to store the frame pointer.
$ra: Register to store the address of the caller of a function (return address).
```

The above list contains 30 register names. The remaining 2 unlisted registers are reserved for use by the operating system. Except for the `$zero` register, which is hardwired to always contain 0, nothing physically distinguishes one register from another and the naming of the registers is just a convention.

## Arithmetic

Take a very simple C code:

```
int a = 1;
int b = 2;
c = a + b;
```

How would you write this code in assembly?

```
addi $s0,$zero,1
addi $s1,$zero,2
add $s2,$s0,$s1
```

`addi` is the "add immediate" instruction. The instruction takes the value in the register given by the second argument and the constant given the third argument and sums them and stores that sum in the register given by the first argument. `add` does a similar operation, but instead of taking a register value and a constant as inputs, it takes 2 register values as inputs.

Notice that instead of explicitly assigning a value to register `$s0` and register `$s1`, we add the value that we want those registers to have to the `$zero` register.

Notice also that we haven't explicitly defined the type of `$s0` and `$s1` anywhere in the assembly program. That's because registers do not have types. Instead, the instruction determines how the register is interpreted. `addi` and `add` interpret the given register values as signed integers. In contrast, `addiu` and `addu` interpret the given register values as unsigned integers.

## Loading and storing data

Beyond instructions to the processor to manipulate data and move data back and forth between the processor and memory, there are also "directives" in assembly, which we can use to store data in memory. You may ask what is the difference between a directive and an instruction? Doesn't a directive have to get translated into an instruction that loads data into memory? An "object file" (the result of compiling an assembly program) contains binary code for instructions and binary code for data. The operating system loads this object file into memory. The binary code for instructions gets executed, but not the binary code for data. Directives define what goes into binary code for data in the object file (see further discussion [here](https://stackoverflow.com/questions/59913912/how-are-assembly-directives-instructed)).

Now consider the C code:

```
int a[5] = {1,2,3,4,5};
int b = 6
int c = b - a[3];
```

Here's the assembly code:

```
.data
arr: .word 1,2,3,4,5

.text
la $t0,arr
lw $s0,12($t0)
addi $s1,$zero,6
sub $s2,$s1,$s0
```

The ".data" section is the section for directives. The ".text" section is the section for instructions. `la` is a pseudo-instruction to load an address into a register. `lw` is an instruction to load a "word" (the number of bits that a register can hold) from memory into a register. The `12($t0)` in that instruction says to move 12 bits from the address stored in register `$t0`. The address `arr` points to the first byte of the array. We move 12 bits, because that represents 3 integers (each integer is 4 bytes).

Now suppose we want to store `c` back in the array:

```
a[4] = c;
```

In assembly, we use `sw`, which is the instruction to store a word in memory:

```
sw $s2,16($t0)
```

## Branching

"A branch is an instruction in a computer program that can cause a computer to begin executing a different instruction sequence and thus deviate from its default behavior of executing instructions in order" ([https://en.wikipedia.org/wiki/Branch_(computer_science)](https://en.wikipedia.org/wiki/Branch_(computer_science)))

There are 2 types of branches: conditional and unconditional branches.

Take the following C code:

```
if (i == j) {
	f = g + h;
} else {
	f = g - h;
}
```

Suppose `$s0` contains the value of f, `$s1$` contains the value of g, `$s2$` contains the value of h, `$s3$` contains the value of i, and `$s4$` contains the value of j.

In assembly, we have:

```
bne $s3,$s4,ElseLabel
add $s0,$s1,$s2
j ExitLabel
ElseLabel: sub $s0,$s1,$s2
ExitLabel: ...
```

`bne` stands for branch not equal. Its first two arguments are registers. If the values in those registers are equal, then the program just continues as normal executing the next instruction. Otherwise, the program jumps to the label given by the third argument. The `bne` instruction here is an example of a conditional branch.

`j` stands for jump. It takes a label as its argument and jumps to that label in the program. The `j` instruction here is an example of an unconditional branch.

## Functions

Here's an example of a simple function in C:

```
int sum(int x, int y) {
	return x + y;
}
```

And its translation into MIPS:

```
add $a0,$s0,$zero
add $a1,$s1,$zero
jal sum
...
sum: add $v0,$a0,$a1
jr $ra
```

The registers `$a0`-`$a3$` are reserved for storing the arguments for function calls. In this case, we store `x` and `y` in `$a0` and `$a1` (assuming we had their values saved in the `$s0` and `$s1` registers).

`jal` stands for jump and link. It should really be called link and jump. It stores the address of the instruction after it in the `$ra` register ("return address" register) and then it jumps to the given label. In this case, it stores the address after "jal sum" and then jumps to the "sum" label.

The sum label adds the function arguments and stores the result in register `$v0`. The registers `$v0` and `$v1` are reserved for storing the return values for function calls.

`jr` on the next line is the "jump register" instruction. It jumps to the address stored in the register supplied to the instruction. In this case, we jump to the address stored in `$ra`, where we've already stored the instruction after "jal sum". In this way, we return control back to the caller of the function.

Note that the way that the functions are defined in MIPS is mostly a matter of following conventions. There are some registers reserved for the arguments of functions and their return values, but otherwise it's just a matter of jumping to another part of the code, managing which data goes into which registers and then jumping back.

What happens when a function calls another function?

We introduce some more conventions. The function must preserve the values of the following registers: `$ra`, `$sp`, `$gp`, `$fp` and `$s0`-`$s7`. The function can manipulate the values of those registers, but has to restore them before jumping back to the return address if it does. The function can change the values of the following registers: `$v0`,`$v1`,`$a0`-`$a3` and `$t0`-`$t9`.

Take the following C code as an example:

```
int sumSquare(int x, int y) {
	return mult(x, x) + y;
}
```

And its translation in assembly:

```
# push
addi $sp,$sp,-8	# space on stack
sw $ra, 4($sp)	# save return address
sw $a1, 0($sp)	# save y

add $a1,$a0,$zero # mult(x,x)
jal mult # call mult
lw $a1, 0($sp) # restore y

# pop
add $v0,$v0,$a1 # mult() + y
lw $ra, 4($sp)	# get ret addr
addi $sp,$sp,8	# restore stack
jr $ra

mult: ...
```

## Sources

* UC Berkeley, CS61C, Spring 2015
	* [Lecture 5](https://www.youtube.com/watch?v=VwmY6K4O2yw&list=PLhMnuBfGeCDM8pXLpqib90mDFJI-e1lpk&index=5)
	* [Lecture 5](https://www.youtube.com/watch?v=VwmY6K4O2yw&list=PLhMnuBfGeCDM8pXLpqib90mDFJI-e1lpk&index=6)