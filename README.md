# 1eft

A programming language designed exclusively for the left hand on a QWERTY keyboard.

## Rules

All characters inside the 1eft language must be a character that is typed with the left hand while touch typing on a QWERTY keyboard (including numbers). The only exception to this rule is within a comment or string literal.
![image](https://github.com/user-attachments/assets/6c3abb7d-ddf4-4bf5-85a3-7f86a844b8f5)

## Keywords

| Keyword | Definition | Example |
|:-|:---|:---|
| **dt** | Decimal Type (32-bit Integer) | ```dt dec eqs 44$``` |
| **ety** | Empty (Like void in C) | See below |
| **def** | Define a function | ```def ety stare dt dec %s exec set dec eexec~ %e```|
| **ret** | Return a value from a function | ```ret 15$``` |
| **exec** | Execute Function | ```exec set1 `Hello World` eexec$```|
| **eexec** | End Argument List for Function | See above |

## Punctuators

| Punctuator | Definition |
|:-|:---|
| **``** | String Literal (Like "" in C) |
| **$** | End Line (Like ";" in C) |
| **%s** | Start Scope (Like "{" in C) |
| **%e** | End Scope (Like "}" in C) |
| **a** | Addition |
| **s** | Subtraction |
| **t** | Times (Multiplication) |
| **d** | Division |
| **eqs** | Assignment Operator (=) |

## Language Predefined Functions

| Function | Usage | Example |
|:-|:---|:---|
| **set** | Set (print) a literal or variable | ```exec set 15 eexec$```|
| **set1** | Set (print) a literal or variable with a new line character at the end | ```exec set1 `Hello World` eexec$``` |
