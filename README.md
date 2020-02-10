# RiSC-16_assembler
## Overview
The Ridiculously-Simple Computer Instruction Set Architecture is a 16-bit, pedagogical ISA developed and specified at the University of Maryland by [Bruce Jacob](https://user.eng.umd.edu/~blj/), who himself based it on Peter Chen's Little Computer 896 (LC-896), developed at the University of Michigan.

The RiSC-16 is an 8-opcode and 8-register ISA with halfword (2-byte) addresses. The complete architecture is detailed in the four-page document found [here](https://user.eng.umd.edu/~blj/RiSC/RiSC-isa.pdf). 

As far as I know, no assembler had yet been written for RISC-16 in Python by the time I began this project. This was just as well; I hope to eventually implement and simulate this ISA in Verilog, for which I would need an assembler, anyway. While I could have written this one in C, in general, I find it much easier to parse and emit text in Python, not to mention that object-oriented programming lends itself quite naturally to tokenization.

## Features
This assembler essentially falls into the two-pass category, which I more or less learned about after skimming Chapter 1 of David Salomon's [*Assemblers and Loaders*](http://www.davidsalomon.name/assem.advertis/AssemAd.html). The two passes are described as follows:

1. *Symbolization*&mdash;the assembler generates a symbol table and populates it with the name and PC of every defined label.
2. *Generation*&mdash;the assembler emits machine code, consulting the symbol table for symbolic operands and addresses.

The first is accomplished by the *symbolizer*, the second by the *generator*. In my implementation, these two are actually explicitly preceded by a *lexer*, which atomizes the source assembly text and creates a list of syntax tokens, including, but not limited to:

* *WhitespaceToken*&mdash;a generic field delimiter (commas, tabs, and spaces are all included)
* *LabelToken*&mdash;an alphanumeric name followed by a colon
* *DirectiveToken*&mdash;any one of the assembler directives nop, halt, lli, movi, .fill, and .space
* *InstructionToken*&mdash;recognized opcodes
* *RegisterToken*&mdash;registers may be preceded by a 'r'
* *Un/SignedImmediateToken*&mdash;may be symbolic and may also be specified in octal, decimal, or hexadecimal

These syntax tokens allow the lexer to condition on partially-parsed assembly and issue errors:

* *SyntaxError*&mdash;invalid constructions, missing arguments, illegal characters, unrecognized registers
* *ValueError*&mdash;signed-unsigned immediate error, immediates and addresses out of bounds

Some error-detection is also built into the symbolizer and generator: for example, the generator will issue a SyntaxError if it encounters an undefined label.

All errors come with an associated error message and a reference to the source line where they were detected (for now, all errors are critical and the assembler will immediately abort upon encountering them). 

## Usage
Clone the repository to your local machine with

```linux
git clone https://github.com/brekekekex/RiSC-16_assembler.git
```

Running the assembler is fairly self-explanatory:
```linux
python assembler.py -h
usage: assembler.py [-h] [--vl] [--vs] [--novg] [--bin] filename

positional arguments:
  filename

optional arguments:
  -h, --help  show this help message and exit
  --vl        verbose lexer--show tokenization
  --vs        verbose symbolizer--show symbol table
  --novg      no verbose generator--do not output object code to console (will
              still write to file)
  --bin       write to target file in binary
```

## Tests

### Generic Lexer 
Assemble (notice irregular whitespace, delimitation, and comments):
```
caller:   beq r0 r0,  callee # unconditional jump (not using jalr)
  callee: halt  # stop machine, dump core
```
Output with --vl:

![alt text](https://github.com/brekekekex/RiSC-16_assembler/blob/master/tests/lexer_test.png)

### Generic Symbolizer
Assemble:
```
null: nop
one:  .fill 1
two:  .fill 2
three: .fill 3
four: .fill 4
five: .fill 5
```
Output with --vs:

![alt text](https://github.com/brekekekex/RiSC-16_assembler/blob/master/tests/symbolizer_test.png)

### Generic Generator
Assemble:
```
# Taken from classweb.ece.umd.edu/enee646.F2011/p1.pdf
  lw 1, 0, count # load reg1 with 5 (uses symbolic address)
  lw 2, 1, 2     # load reg2 with -1 (uses numeric address)
start: add 1, 1, 2  # decrement reg1 (could have been 'addi 1, 1, -1')
  beq 0, 1, start # changed from bne to beq
done: halt
  nop
count: .fill 5
neg1:  .fill -1
startAddr: .fill start
```
Output:

![alt text](https://github.com/brekekekex/RiSC-16_assembler/blob/master/tests/generator_test.png)

### Generic SyntaxErrors
Assemble:
```
foo: beq r0, r0, bar
```
Output:

![alt text](https://github.com/brekekekex/RiSC-16_assembler/blob/master/tests/label_error.png)

Assemble:
```
add r0, r1
```
Output:

![alt text](https://github.com/brekekekex/RiSC-16_assembler/blob/master/tests/syntax_error.png)

### Generic ValueError
Assemble:
```
  addi r1, r0, 34234
```
Output:

![alt text](https://github.com/brekekekex/RiSC-16_assembler/blob/master/tests/value_error.png)





