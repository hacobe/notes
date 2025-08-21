# Branch prediction

Consider the following assembly program:

```assembly
global _main
section .text
_main:
    MOV rdi, 5
    CMP rdi, 3
    JG greater
    MOV rax, 0
    JMP done
greater:
    MOV rax, 1
done:
    RET
```

The processor pipelines the instructions through the Fetch, Decode and Execute stages.

**No branch prediction**

Without branch prediction, the processor waits until `JG greater` reaches the Execute stage in Cycle 5. At that point, it knows which instruction it needs to fetch and does so in Cycle 6. In this case, we have 6 cycles idle.

| Stage   | Cycle 1 | Cycle 2 | Cycle 3 | Cycle 4 | Cycle 5 | Cycle 6 | Cycle 7 | Cycle 8 | Cycle 9 |
|---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|
| Fetch   | MOV rdi | CMP rdi | JG      | -       | -       | MOV rax,1| RET | -       | -       |
| Decode  | -       | MOV rdi | CMP rdi | JG      | -       | -       | MOV rax,1| RET | -       |
| Execute | -       | -       | MOV rdi | CMP rdi | JG      | -       | -       | MOV rax,1| RET |

**Correct branch prediction:**

With correct branch prediction, the processor guesses that the program will jump in Cycle 4 and fetches the `MOV rax, 1` instruction in Cycle 5. In this case, we have no idle cycles.

| Stage   | Cycle 1 | Cycle 2 | Cycle 3 | Cycle 4 | Cycle 5 | Cycle 6 | Cycle 7 |
|---------|---------|---------|---------|---------|---------|---------|---------|
| Fetch   | MOV rdi | CMP rdi | JG      | MOV rax,1| RET | -       | -       |
| Decode  | -       | MOV rdi | CMP rdi | JG      | MOV rax,1| RET | -       |
| Execute | -       | -       | MOV rdi | CMP rdi | JG      | MOV rax,1| RET |

**Incorrect branch prediction:**

With incorrect branch prediction, the processor incorrectly guesses that the program won't jump in Cycle 4 and fetches the `MOV rax, 0` instruction. In Cycle 5, it fetches the `JMP done` instruction, decodes the `MOV rax, 0` instruction and executes `JG greater` instruction only to find out it guessed incorrectly. In Cycle 6, it flushes the pipeline. In Cycle 7, it starts with the correct instruction (`MOV rax, 1`). In this case, we have 6 cycles idle or executing an instruction that ultimately gets discarded.

| Stage   | Cycle 1 | Cycle 2 | Cycle 3 | Cycle 4 | Cycle 5 | Cycle 6 | Cycle 7 | Cycle 8 | Cycle 9 |
|---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|
| Fetch   | MOV rdi | CMP rdi | JG      | MOV rax,0| JMP    | MOV rax,1| RET    | -       | -       |
| Decode  | -       | MOV rdi | CMP rdi | JG      | MOV rax,0| -      | MOV rax,1| RET    | -       |
| Execute | -       | -       | MOV rdi | CMP rdi | JG      | -       | -       | MOV rax,1| RET    |
