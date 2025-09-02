# 1eft

A programming language designed exclusively for the left hand on a QWERTY keyboard.

## Rules

All characters inside the 1eft language must be a character that is typed with the left hand while touch typing on a QWERTY keyboard (including numbers and newline characters). The only exception to this rule is within a comment or string literal.
![image](https://github.com/user-attachments/assets/6c3abb7d-ddf4-4bf5-85a3-7f86a844b8f5)

## Numbers

The numbers 1-5 are the only numbers allowed to be typed in the 1eft language. Since "0" is not allowed, the "@" symbol acts as a 0. The numbers 6-9 are represented as a-d respectively (6 is a, 7 is b, etc.). To write a number, the number must start with the prefix %d and end with the suffix !d. Example: The number 1234567890 is ```%d12345abcd@!d```

## Keywords

| Keyword | Definition | Example |
|:-|:---|:---|
| **dect** | Decimal Type (32-bit Integer) | ```dect dec ass %d44!d$``` |
| **v@1d** | Void (Like void in C) | See below |
| **def** | Define a function | ```def v@1d stare dect dec %s exec set %e dec !e$ !s```|
| **ret** | Return a value from a function | ```ret %d15!d$``` |
| **exec** | Execute Function | ```exec wr1te1 %e `Hello World` !e $```|

## Punctuators

| Punctuator | Definition |
|:-|:---|
| **``** | String Literal (Like "" in C) |
| **$** | End Line (Like ";" in C) |
| **%s** | Start Scope (Like "{" in C) |
| **!s** | End Scope (Like "}" in C) |
| **%e** | Start Expression (Like "(" in C) |
| **!e** | End Expression (Like ")" in C) |
| **%d** | Start Decimal |
| **!d** | End Decimal |
| **a** | Addition |
| **s** | Subtraction |
| **t** | Times (Multiplication) |
| **d** | Division |
| **ass** | Assignment Operator (=) |

## Language Predefined Functions

| Function | Usage | Example |
|:-|:---|:---|
| **wr1te** | Print a string literal | ```exec wr1te %e `abc` !e$```|
| **wr1te1** | Print a string literal with a new line character at the end | ```exec wr1te1 %e `Hello World` !e$``` |
| **wr1ted** | Print a decimal type (literal or variable) | ```eexec wr1ted %e %d15!d$ !e```|
