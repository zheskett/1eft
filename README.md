# 1eft

A programming language designed exclusively for the left hand on a QWERTY keyboard.

## Rules

All characters inside the 1eft language must be a character that is typed with the left hand while touch typing on a QWERTY keyboard (including numbers and newline characters). The only exception to this rule is within a comment or string literal.

![image](https://github.com/user-attachments/assets/6c3abb7d-ddf4-4bf5-85a3-7f86a844b8f5)

## Numbers

The numbers 1-5 are the only numbers allowed to be typed in the 1eft language. Since "0" is not allowed, the "@" symbol acts as a 0. The numbers 6-9 are represented as a-d respectively (6 is a, 7 is b, etc.). To write a number, the number must start with the prefix %d and end with the suffix !d. Example: The number 1234567890 is ```%d12345abcd@!d```

## Strings

String literals are enclosed in backticks (``` ` ```). For example: ``` `1eft !s best` ```. Any character is allowed in a string literal, including characters on the right hand side of the keyboard. When stored in a ```car``` variable, a the variable will only store the first character of the string. To store multiple characters, use a ```char#``` variable.

## Keywords

| Keyword | Definition | Example |
|:-|:---|:---|
| **```trve```** | True Value (Boolean) | ```var ass trve$``` |
| **```fa1se```** | False Value (Boolean) | ```var ass fa1se$``` |
| **```b@11```** | Boolean Type (True/False) | ```b@11 var$``` |
| **```dect```** | Decimal Type (32-bit Integer) | ```dect dec$``` |
| **```car```** | Character Type (Text) | ```car var$``` |
| **```v@1d```** | Void (Like void in C) | See below |
| **```def```** | Define a function | ```def v@1d stare dect dec %s exec set %e dec !e$ !s```|
| **```ret```** | Return a value from a function | ```ret %d15!d$``` or ```ret$```|
| **```exec```** | Execute Function | ```exec wr1te1 %e `Hello World` !e $```|
| **```bass```** | No Operation (Like "pass" in Python) | ```bass $``` |
| **```1f```** | If Statement | ```1f %d1!d eq %d1!d %s var ass %d1!d$ !s``` |
| **```e1se```** | Else Statement | ```1f %d1!d eq %d1!d %s var ass %d1!d$ !s e1se %s var ass %d@!d$ !s``` |
| **```e1se1f```** | Else If Statement | ```1f fa1se %s var ass %d1!d$ !s e1se1f trve %s var ass %d@!d$ !s``` |
| **```as```** | As Loop (While Loop) | ```as var lt %d1@!d %s var ass var s %d1!d$ !s``` |

## Punctuators

| Punctuator | Definition |
|:-|:---|
| **``` `` ```** | String Literal (Like "" in C) |
| **```$```** | End Line (Like ";" in C) |
| **```%s```** | Start Scope (Like "{" in C) |
| **```!s```** | End Scope (Like "}" in C) |
| **```%e```** | Start Expression (Like "(" in C) |
| **```!e```** | End Expression (Like ")" in C) |
| **```%d```** | Start Decimal |
| **```!d```** | End Decimal |

## Operators

IMPORTANT NOTE: OPERATORS MUST HAVE SPACES ON BOTH SIDES!

| Operator | Definition |
|:-|:---|
| **```ass```** | Assignment Operator (=) |
| **```#```** | Pointer or Dereference Symbol (Like "*" in C) |
| **```addr```** | Address of Operator ("&" in C) |
| **```rev```** | Reverse (Not) Operator (```rev fa1se```)|
| **```sf@```** | Subtract From 0 (Negation) Operator (```sf@ %d1!d```) |
| **```a```** | Addition |
| **```s```** | Subtraction |
| **```t```** | Times (Multiplication) |
| **```d```** | Division |
| **```%%```** | Modulus |
| **```eq```** | Equality Operator (==) |
| **```req```** | Reverse Equal Operator (!=) |
| **```1t```** | Less Than Operator (<) |
| **```gt```** | Greater Than Operator (>) |
| **```1te```** | Less Than or Equal To Operator (<=) |
| **```gte```** | Greater Than or Equal To Operator (>=) |
| **```@@```** | And Operator (&&) |
| **```@r```** | Or Operator (\|\|) |

## Language Predefined Functions

| Function | Usage | Example |
|:-|:---|:---|
| **```wr1te```** | Print a char# | ```exec wr1te %e `abc` !e$```|
| **```wr1te1```** | Print a char# with a new line character at the end | ```exec wr1te1 %e `Hello World` !e$```|
| **```wr1ted```** | Print a decimal type | ```exec wr1ted %e %d15!d$ !e```|
| **```wr1teb```** | Print a boolean type | ```exec wr1teb %e trve !e$```|
| **```wr1tec```** | Print a char type | ```exec wr1tec %e `A` !e$```|
| **```wr1tea```** | Print an address (pointer) | ```exec wr1tea %e addr var !e$```|
| **```getd```** | Get a decimal from stdin (No arguments)| ```exec getd %e!e$```|
| **```srazd```** | Seed the random number generator (auto seeded with time at program start) | ```exec srazd %e %d12345!d !e$```|
| **```razdd```** | Get a random decimal between 0 and 32-bit integer maximum | ```var ass exec razdd %e!e$ %% %d!5d$``` |
