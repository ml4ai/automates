Briefly, the problem of source code summarization is that of using a
machine reading system to read a piece of source code (such as a
function) and subsequently generate a summary description of it in
natural language. Below is an outline of several tasks that we have
undertaken to develop a tool capable of accomplishing this, as well as
tasks that we plan to undertake in the near future to extend the
capabilities of our tool.

### Problem definition

We seek to develop a tool that reads a source code function and outputs
a high-level descriptive summary of the function. For our purposes a
source code function is defined to be any source code block that human
readers would normally consider to be a standalone unit of code. For our
target codebase, [DSSAT](https://dssat.net) (which is written in
Fortran) this will translate to being any discovered subroutine or
function contained in the codebase. It is important to note that the
method we develop will need to be able to handle functions of various
sizes.  A second important note is that our method will need to be able
to handle functions with a variety of purposes, ranging from scientific
computations to file system access.

### Function-docstring corpus

To create a tool capable of handling the two problems described above
associated with the functions we are likely to see, we need a large
corpus of functions with associated natural language summary
descriptions. Our target source code language for this corpus will be
the Python programming language, for the following reasons:

1. `for2py` will be converting all of the Fortran code we intend to
   summarize from DSSAT into Python code. The summary comments found in
   DSSAT will be converted to Python docstrings (a Python docstring is a
   natural language comment associated with a function that contains a
   descriptive summary of the function).
2. Python has a standard format for docstrings encapsulated by the [PEP
   257](https://www.python.org/dev/peps/pep-0257/) style guidelines.
   This ensures that the source code functions we find in Python will
   have consistent styling rules for their associated summaries.
3. Python has a vast and varied collection of packages that have large
   numbers of functions with a variety of purposes. Even better, these
   packages are often neatly categorized in lists such as the [awesome
   Python list].  This will come in handy for adapting our summary
   generator to dealing with functions that compute a variety of tasks
4. Python lacks many syntactic features that would ease the process of
   translation. For example, Python lacks type hints which means that a
   summary generator targeted at Python will be forced to learn the
   semantics behind the language without straightforward syntactic
   mappings.

To construct a corpus of Python function-docstring pairs for the purpose
of training our summary generator model we created a tool called
`CodeCrawler`.  `CodeCrawler` is capable of indexing entire Python
packages to find all functions contained in the recursive module
structure. Once all of the functions have been found, `CodeCrawler`
proceeds to check each function for a PEP 257 standard docstring. For
functions that meet this qualification, the code is tokenized and the
docstring is shortened to only the function description, which is then
also tokenized. These two items then make one function-dosctring
instance in our corpus. Currently our corpus has a total of 21,306
function-docstring pairs discovered from the following Python packages:
`scikit-learn`, `numpy`, `scipy`, `sympy`, `matplotlib`, `pygame`,
`sqlalchemy`, `scikit-image`, `h5py`, `dask`, `seaborn`, `tensorflow`,
`keras`, `dynet`, `autograd`, `tangent`, `chainer`, `networkx`,
`pandas`, `theano`, and `torch`.

### Summary generator

A myriad of tools already exist that claim to solve the problem of
source code summarization. The current state-of-the-art tool is
[Code-NN](https://aclweb.org/anthology/P/P16/P16-1195.pdf), a neural
encoder-decoder method that produces a one-line summary of a short
(fewer than 10 lines) source code snippet. We have implemented and
extended Code-NN to form our summary generator model. Below we describe
the details of how we have extended the model as well as a rationale
explaining the model extensions.

#### Encoder-decoder architecture

We have made two large changes to the encoder-decoder architecture
proposed by Code-NN in order to adapt the model to our specific
summarization task. As stated above, Code-NN operates over very small
code-snippets of no more than 10 lines of code. Our summary generator
needs to be able to summarize functions that commonly are between 20 -
50 lines of code, with far more symbols per line.  To accomplish this
task we needed to change the source code encoder architecture to account
for the larger input size. Code-NN uses a standard
[LSTM](https://www.ncbi.nlm.nih.gov/pubmed/9377276) architecture to
encode information about the source code into an internal representation
that can be decoded into a descriptive summary. The problem with using a
base LSTM is that an LSTM has a memory limit that harms performance on
large input sequences. The standard solution to such a problem is to use
a [bidirectional
LSTM](https://pdfs.semanticscholar.org/4b80/89bc9b49f84de43acc2eb8900035f7d492b2.pdf)
to avoid the memory limitation issue. Thus we replace Code-NN's LSTM
encoder with a bidirectional LSTM. Secondly, since our functions are
considerably longer we suspect that the descriptive summaries may
contain hierarchical semantic meaning, and thus we have replaced the
decoder LSTM used in Code-NN with a stacked-LSTM that will be able to
capture hierarchical semantics.

#### Pre-trained word embeddings

The bread and butter of any neural-network based translation tool is the
semantic information captured by word embeddings. Word embeddings
represent single syntactic tokens in a language (source code or natural
language) as a vector of real numbers, where each syntactically unique
token has its own vector.  The distance between vectors, as measured by
[cosine similarity](https://en.wikipedia.org/wiki/Cosine_similarity), is
meaningful and is used to denote semantic similarity between tokens.
When using word embeddings in a neural model the word embeddings can
either be [learned with the model](https://arxiv.org/pdf/1301.3781.pdf)
or pre-trained via a classic word embedding algorithm such as
[word2vec](https://papers.nips.cc/paper/5021-distributed-representations-of-words-and-phrases-and-their-compositionality.pdf).
We have decided to test our model both with and without pre-training the
word embeddings. Due to the small size of our corpus, it is likely that
the model with pre-trained embeddings will perform better.

#### Evaluation metrics

Fundamentally, source code summarization is a translation problem. We
are transforming the source code into a natural language summary. Thus,
for automatic evaluation of our model we will use the industry standard
evaluation metric, the [BLEU
score](https://www.aclweb.org/anthology/P02-1040.pdf). This uses a
collection of modified _n-gram_ precision methods to compare a
model-generated summary to an existing human-generated 'gold standard'
summary.

Along with this automatic method we will also select examples at random from our
corpus to be analyzed by linguistic experts. This will give us a qualitative
intuition of model performance on the summarization task.


### Planned extensions

After running our initial tests with our summary generator model over our
function-docstring corpus we discovered that our results are less than
satisfactory. To improve our models performance we have outlined several
improvements that we will be implementing during the course of the project.
Below is a short description of each improvement we seek to make to our summary
generator.

#### Increase corpus size

As we continue to test our summary generator we can use our `CodeCrawler` to
search through more Python packages in the [awesome Python list]. Adding
additional function-docstring pairs to our corpus should greatly improve model
performance.

#### Domain adaptation information

Once a large enough amount of Python packages has been added to our corpus we
can begin segmenting our corpus by domain. The domains chosen for a particular
Python package will match the domains assigned to the package by the [awesome
Python list]. Once our corpus has been separated into domains we can apply
[domain
adaption](http://legacydirs.umiacs.umd.edu/~hal/docs/daume07easyadapt.pdf)
techniques to our encoder-decoder model in order to begin modeling domain
differences that will allow of summary generator to generate more accurate
domain-specific summaries for source code functions.

#### Character Level embeddings

Many symbols in our source code language occur with a frequency too low
to be embedded properly in our word embeddings. Unfortunately these
symbols tend to be the names of variables and the functions themselves,
items which are very important to the summarization task! Without good
word embeddings for these items it is hard to learn the semantic
information associated with them. In other NLP tasks a remedy for this
issue is to use character embeddings so that at least some signal is
sent from these tokens. For the case of source code, character
embeddings are especially useful because they can encode implied
semantics of variable names, such as whether they are written in
`snake_case`, `camelCase`, or `UpperCamelCase`. For these reasons,
adding character embeddings to our summary generator is high on our
priority list.

#### Tree-structured code encoding

Currently our summary generator reads a flat syntactic
representation of source code. However, we can easily extract an
abstract syntax tree from our source code that will encode semantic
information in the tree structure itself.  This information may prove
useful to the task of summarization, and thus we are investigating the
architectural changes necessary to incorporate such information.

[awesome Python list]: https://github.com/vinta/awesome-Python#cluster-computing
