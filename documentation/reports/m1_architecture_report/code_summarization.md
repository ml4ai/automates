## 6. Code Summarization

Briefly, the problem of source code summarization is that of using a
machine reader system to read a piece of source code (such as a
function) and subsequently generate a summary description of it in
natural language. Below is an outline of several tasks that we have
undertaken to develop a tool capable of accomplishing this, as
well as tasks that we plan to undertake in the near future to extend the
capabilities of our tool.

### Problem definition

A myriad of tools already exist that claim to solve the problem of
source code summarization. The current state-of-the-art tool is
[Code-NN](https://aclweb.org/anthology/P/P16/P16-1195.pdf), a neural
encoder-decoder method that produces a one-line summary of a short
(fewer than 10 lines) source code snippet. Unfortunately this is not as
general as the problem we seek to solve. Our target codebase, DSSAT,
uses large subroutines, and thus the tool we develop will need to be
able to handle full-formed functions of varying size. To that end we
have adapted the Code-NN tool to fit our purposes but

### Function-docstring training corpus



### Summary generator

#### Encoder-decoder architecture

#### Pre-trained word embeddings

#### Evaluation metrics



### Planned extensions

#### Domain adaptation information

#### Character Level embeddings

#### Tree-structured code encoding
