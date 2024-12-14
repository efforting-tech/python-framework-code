# Current plan


## Method for template engine
Define tokens that will handle both indention levels per line and also special tokens for inline expressions.

## Tokens
- Indention is regex `^(\s*)`
- Newline is `\n`

> [!NOTE]
> We will use zero width matching for indention tokens to ensure that every line always starts with an indention token.


## Text document
A text document is an immutable array of tokens.

## Line index
The line index is an array of slices that represents the tokens of the text document.

## Text blocks
Is a sub section of the line array of a text document. A slice.

## Text line
Is an array of tokens.

## Goals
- A working template engine
	+ Supports indention matching
