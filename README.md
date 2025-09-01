# 1eft

A programming language designed exclusively for the left hand on a QWERTY keyboard.

## Rules

All characters inside the 1eft language must be a character that is typed with the left hand while touch typing on a QWERTY keyboard (including numbers). The only exception to this rule is within a comment or string literal.
![image](https://github.com/user-attachments/assets/6c3abb7d-ddf4-4bf5-85a3-7f86a844b8f5)

## Numbers

The numbers 1-5 are the only numbers allowed to be typed in the 1eft language. Since "0" is not allowed, the "@" symbol acts as a 0. The numbers 6-9 are represented as a-d respectively (6 is a, 7 is b, etc.). To write a number, the number must start with the prefix @d. Example: The number 1234567890 is ```@d12345abcd@```

## Keywords

| Keyword | Definition | Example |
|:-|:---|:---|
| **dect** | Decimal Type (32-bit Integer) | ```dect dec eqs 44$``` |
| **v@!d** | Void (Like void in C) | See below |
| **def** | Define a function | ```def ety stare dect dec %s exec set dec eexec~ %e```|
| **ret** | Return a value from a function | ```ret 15$``` |
| **exec** | Execute Function | ```exec wr1te1 `Hello World` eexec$```|
| **eexec** | End Argument List for Function | See above |

## Punctuators

| Punctuator | Definition |
|:-|:---|
| **``** | String Literal (Like "" in C) |
| **$** | End Line (Like ";" in C) |
| **%s** | Start Scope (Like "{" in C) |
| **!s** | End Scope (Like "}" in C) |
| **a** | Addition |
| **s** | Subtraction |
| **t** | Times (Multiplication) |
| **d** | Division |
| **eqs** | Assignment Operator (=) |

## Language Predefined Functions

| Function | Usage | Example |
|:-|:---|:---|
| **wr1te** | Print a string literal | ```exec wr1te `abc` eexec$```|
| **wr1te1** | Print a string literal with a new line character at the end | ```exec wr1te1 `Hello World` eexec$``` |
| **wr1ted** | Print a decimal type (literal or variable) | ```eexec wr1ted 15 eexec$```|
