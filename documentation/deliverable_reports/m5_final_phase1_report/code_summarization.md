## Code Summarization

The goal of the Code Summarization module is to provide one or more methods to
automatically generate natural language descriptions of components of source
code. Work in Phase 1 has been devoted to evaluating and make an initial
adaptation in application of the state of the art `Sequence2Sequence` neural
machine translation (NMT) model described in [_Effective Approaches to
Attention-based Neural Machine
Translation_](https://arxiv.org/pdf/1508.04025.pdf), an encoder-decoder method
for machine translation that utilizes Bi-LSTM recurrent networks over each of
the input sequences to map sequences in one language to another. In the [Month
3 Report on Code
Summarization](/documentation/deliverable_reports/m3_report_prototype_system/#code-summarization)
we presented the initial empirical results of training the NMT model on a
training/evaluation corpus we developed, starting with training the code and
language embedding models (the initial encodings of the source and target
domains). We evaluated the capacity of the embeddings to perform a simpler
"relevant/not-relevant" document classification task, which helps us assess
whether the embeddings are learning information relevant to code summarization.
Since the Month 3 report, we have continued evaluating the model and here
summarize lessons learned so far. So far, our results in raw generation are low
quality, but this is still very early and we have several different directions
to take. This has also led us to consider some alternative approaches to code
summarization that we will explore in the next phase of the program.  In
this section we review the experiments we have performed, discuss the
limitations of the current neural methods, and end with description of how to
obtain and process the data and train the models in our initial Prototype
release.

### Dataset overview

The [NMT model](https://arxiv.org/pdf/1508.04025.pdf) was originally developed
and evaluated on data where the code sequences to be summarized are relative
small: on the order of under 100 source code tokens. Source code tokens are the
result of the pre-processing used in NLP before embedding: identifying what
constitutes a "word", and to the extent possible, resolving variant spellings
or expressions of the same concept as a single token. In our application,
functions tend to have an order of magnitude more source code tokens: around
1000. For this reason, we need to identify a suitable corpus of larger source
code segments with associate docstring summaries, and the corpus needs to be
large. We extracted a very large corpus of Python function / docstring pairs by
scraping the entirety of the [awesome-python](https://awesome-python.com) list
of Python packages, extracting function source code and their associated
docstrings.
In order to automate the function / docstring extraction while attempting to
find higher quality docstring descriptions paired with source code, we created
a tool called CodeCrawler. The processing pipeline for CodeCrawler is shown in
Figure 22.

![Code Crawler architecture](figs/code_summ/code-crawler.png)

**Figure 22:** Code Crawler architecture.

The pipeline consists of these components:

- **Function finder**: This component uses Python's built-in `inspect` module
  to find all function signatures in a Python module. The `inspect` module also
  has the ability to grab the docstring associated with a function using the
  `__doc__` variable.

- **Paired docstring finder**: This component determines whether the docstring
  returned from the `__doc__` attribute qualifies as a descriptive function
  comment. To do this, we check the docstring to see if it conforms to the [PEP
  257](https://www.python.org/dev/peps/pep-0257/) standards for docstrings, in
  an attempt to generally find higher quality comments, under the assumption
  that docstrings formatted in this way will tend to be higher quality. If the
  docstring conforms, we then use the function description section as our
  descriptive docstring.

- **Source code cleaner**: Code summarization methods generally try to learn to
  map from source code vocabulary tokens (what terms are used in code) to a
  natural language description. In general, this task is easier when the source
  code vocabulary is observed repeatedly under different conditions in the
  corpus. In order to reduce the number of unique source code vocabulary terms
  (and thereby increase the frequency with which each term is observered), this
  component "cleans" the function code by the following rules:
  - All identifiers are split based on `snake_case` and `camelCase` rules.
  - All numbers are separated into digits (e.g., 103 becomes 1, 0, 3).
  - All string literals were replaced with the token `<STRING>`.

- **Docstring cleaner**: Following the same intuition as the source code
  cleaner, the docstring cleaner is responsible for removing all parts of the
  docstring that are not specified as descriptive, according to [PEP
  257](https://www.python.org/dev/peps/pep-0257/) standards. This is
  accomplished with simple pattern matching on the docstring.

Using CodeCrawler, we found a total of 76686 Python functions with well-formed
docstrings.

### Experimental results

In the [Month 3 Report on Code
Summarization](https://ml4ai.github.io/automates/documentation/deliverable_reports/m3_report_prototype_system/#code-summarization),
we presented the initial results of training and evaluating the embedding layer
to the NMT model using the corpus extracted by the CodeCrawler. To evaluate
whether the trained embeddings appear to be capturing information about the
relationship of source code features to natural language summaries, we first
created a simple classification task that evaluates the ability of the
embeddings to inform a decision about whether a provided natural language
description is "relevant" to input source code.

As reported in the [Month 3 Report on Code
Summarization](https://ml4ai.github.io/automates/documentation/deliverable_reports/m3_report_prototype_system/#code-summarization),
we created two datasets from our corpus for this classification task. In both
cases, we use the 76686 _positive_ association examples found using
CodeCrawler, but the differences are in how _negative_ function/docstring pairs
are constructed:

- In the first dataset, which we call the _random-draw_ dataset, for each
  source code function to be summarized, we uniformly randomly sampled a
  docstring from the corpus and associated it with the function. We expect
  learning to distinguish positive from negative function/docstring pairings to
  be relatively easy given the general varaince in docstring and code. It is
  possible that some randomly paired docstrings may actually be accurate or at
  least related summaries of the function. But in general, we estimate this
  probability to be low. Verifying this is still a work in progress.

- For the second, _challenge_, dataset, we used a Lucene index over the
  docstrings to then search for docstrings with the highest lexical overlap to
  the true docstring originally associated with the function. This
  classification task is significantly more difficult as now the associated
  "negative" example shares much in common with the original description, but
  must still be distinguished.

For both datasets, we generated 10x more negative examples than the positive examples: 766,860.

By the Month 3 report, we had only just constructed the two datasets and only
had very preliminary results for the _random-draw_ dataset. This phase we
completed this initial study, training the neural network model using both data
sets, in both cases performing a grid search to optimize the hyperparameters.
The results of the two models are summarized in the following table:

| Dataset       | Accuracy | Precision | Recall | F1   |
| :---         | ---:     | ---:      | ---:   | ---: |
| `random-draw` | 89%      | 48%       | 82%    | 60%  |
| `challenge`   | 64%      | 14%       | 61%    | 23%  |

Not surprisingly, the accuracy is generally much higher than the F1 scores due
to the general (and intended) imbalance in the data (10x more negative than
positive examples).

The model achieves fairly high accuracy on the _random-draw_ dataset, and this
is expected given that random code strings will very likely not be relevant to
the code the function has been randomly paired with. The challenge data set,
however, is much more difficult, as reflected in the results. Precision, in
particular, takes a very big hit.

Next, we evaluated the NMT model by training and evaluating the model on our
overall corpus, itself containing soruce code tokens that are generally an
order of magnitude longer than those used in the original NMT evaluation. Here,
we use the [BLEU-4](https://en.wikipedia.org/wiki/BLEU) score as an estimate of
how close the generated natural language summarization is to the original
docsctring associated with the source code. Here we have found that the BLEU-4
score is so far very low: 1.88. It is hard at this point to assess by this
score alone how we're doing as to date this task has not been attempted. But it
does provide a baseline for us to improve on.

In the next section we discuss the lessons learned so far.

### Lessons and next steps

We manually inspected a randomly sampled subset of 100 code/docstring pairs
from our corpus to better understand what might be limiting the current model's
performance and identify how we can adapt the method. Based on these samples,
we now have a few conjectures about the nature our code/docstring corpus.

An assumption we have been making about the corpus is that the function /
docstring pairs it contains are fairly high quality, meaning that the
docstrings do indeed do a good job of summarizing the function. When we
initially inspected this data, it looked to be the case, and our assumption was
that given that these are production quality code bases, the documentation
should generally be high quality. Below are two examples from our corpus that
do meet these standards. The docstrings are descriptive of the actual code in
the functions and the identifiers in the functions can be used to deduce the
proper docstrings.

```python
def __ne__(self, other):
    """Returns true if both objects are not equal"""
    return not self == other

def printSchema(self):
    """Prints out the schema in the tree format."""
    print(self._jdf.schema().treeString())
```

Unfortunately, after gathering the CodeCrawler corpus and taking an unbiased
random sample, we are now finding that many of the functions found in our
corpus had "associative", rather than "descriptive", docstrings, meaning that
the portion of the dosctring that we are recovering, which is intended to be
descriptive according to the PEP 257 standards, merely associates the function
either with some other module-level construct or some real-world phenomena,
rather than summarizing the code itself. Some examples of such functions are
included below. It is easy to see how creating these docstrings would require
outside context and cannot be recovered from the actual source code itself.
While these functions may be ideal for a different task, they are not as
useful, and are far more frequent than we had expected.

```python
def __repr__(self):
    """For `print` and `pprint`"""
    return self.to_str()

def get_A1_hom(s, scalarKP=False):
    """Builds A1 for the spatial error GM estimation
    with homoscedasticity as in Drukker et al."""
    n = float(s.shape[0])
    wpw = s.T * s
    twpw = np.sum(wpw.diagonal())
    e = SP.eye(n, n, format='csr')
    e.data = np.ones(int(n)) * (twpw / n)
    num = wpw - e
    if not scalarKP:
        return num
    else:
        den = 1. + (twpw / n) ** 2.
        return num / den

def is_hom(self, allele=None):
    """Find genotype calls that are homozygous."""

    if allele is None:
        allele1 = self.values[..., 0, np.newaxis]
        other_alleles = self.values[..., 1:]
        tmp = (allele1 >= 0) & (allele1 == other_alleles)
        out = np.all(tmp, axis=-1)
    else:
        out = np.all(self.values == allele, axis=-1)

    if self.mask is not None:
        out &= ~self.mask

    return out
```

Additionally, we have identified a second class of problematic functions in our
corpus, which have docstrings that are "descriptive", but composed mainly of
references to items created in the module hierarchy of the Python module that
the function resides in.  This presents two challenges for docstring
generation.  First, it is expected to include information when generating the
description of a function that is not contained in the function.  This is
illustrated in the first of the two examples below, where a docstring includes
references to the `pandas` and `scipy` libraries.  Such information would never
be included in the source code of a Python function.  The second challenge for
docstring generation is in dealing with module level information.  Python is an
object-oriented language, and thus functions written in Python deal with
objects, and it is expected that programmers inspecting and utilizing the
functions will be aware of those objects.  This additional information is again
outside of the actual function itself and our current docstring generator will
not have access to this information; a good example of this is shown in the
second example below, where the `Point` and `imageItem` class are both objects
at the module level that are referenced by the function.

```python
def sparseDfToCsc(self, df):
    """convert a pandas sparse dataframe to a scipy sparse array"""
    columns = df.columns
    dat, rows = map(list, zip(
        *[(df[col].sp_values - df[col].fill_value,
          df[col].sp_index.to_int_index().indices)
          for col in columns]
    ))
    cols = [np.ones_like(a) * i for (i, a) in enumerate(dat)]
    datF, rowsF, colsF = (
      np.concatenate(dat),
      np.concatenate(rows),
      np.concatenate(cols)
    )
    arr = sparse.coo_matrix(
      (datF, (rowsF, colsF)),
      df.shape,
      dtype=np.float64
    )
    return arr.tocsc()

def getArrayRegion(self, data, img, axes=(0,1), order=1, **kwds):
    """Use the position of this ROI relative to an imageItem to pull a slice
    from an array."""

    imgPts = [self.mapToItem(img, h['item'].pos()) for h in self.handles]
    rgns = []
    for i in range(len(imgPts)-1):
        d = Point(imgPts[i+1] - imgPts[i])
        o = Point(imgPts[i])
        r = fn.affineSlice(
          data,
          shape=(int(d.length()),),
          vectors=[
            Point(d.norm())],
            origin=o,
            axes=axes,
            order=order,
            **kwds
          )
        rgns.append(r)

    return np.concatenate(rgns, axis=axes[0])
```

#### Alternative strategies for code summarization

In summary, we found that many of the code/docstring pairs we have found in our extracted corpus involve docstrings describing code that includes information that also relies on at least one form of additional information not present in the code. The current NMT model assumes that all of the information needed for summarizing is contained within the input code itself. Our lambda functions generated by the AutoMATES pipeline certainly fit this definition, and thus our code/docstring corpus is not a good model for our target generation task.

Based on these lessons, we are considering two new approaches to improving our corpus:

1. We are exploring possible methods to incorporate more of the missing context into the code/docstring corpus. This is not an easy task, but if successful would have high payoff for extending `Sequence2Sequence` models to the much more challenging task of summarizing large code segments, as found more naturally in mature code bases.

2. We are also now exploring rule-based methods for generating function descriptions. In this approach, we aim to take advantage of the highly structured, simplistic, and relative self-contained nature of our generated lambda functions in order programmatically summarize of each lambda functions, in such a way that rule-based summarizations may be composed to form larger descriptions of the original subroutines, with the option to collapse and expand summary details associated with code structure.

### Acquiring the corpus and running the training scripts

The data necessary to replicate our experiments can be downloaded using the
following commands (for *nix systems):

```
curl -O http://vision.cs.arizona.edu/adarsh/automates/code-summ-corpus.zip
```

Unzip the file to expose the contained folder `code-summ-corpus/`, and then set the `CODE_CORPUS` environment variable to point to the data folder:

```
export CODE_CORPUS="/path/to/code-summ-corpus"
```

The code summarization tools require the following Python modules: `numpy`, `torch`, `torchtext`, and `tqdm`. These can all easily be installed using `pip` or `conda`.

##### Running the CodeCrawler tool

To run `CodeCrawler`, you will need to install `nltk` as well. The
`CodeCrawler` tool can be run using this command (assuming you have cloned the automates Github repo):

```
python automates/code_summarization/code-crawler/main.py
```

##### Running the classification experiment scripts

The classification experiments can be run with the following command:

```
python automates/code_summarization/src/main.py [-e <amt>] [-b <amt>] [-c <name>] [-g] [-d] [-t]
```

The flags associated with this command are:

- `-e`: The number of epochs to train the model. Increasing the number of
  epochs will increase the training time, but result in higher accuracy.
- `-b`: The size of a batch for training and testing. Larger batch sizes
  decrease the training time for a model, but can decrease accuracy.
- `-c`: The classification corpus to use, either `rand_draw` or `challenge`
- `-g`: GPU availability. Include this flag if your system has an Nvidia GPU
- `-d`: Development set evaluation. Include this flag to evaluate the model on
  the development set.
- `-t`: Test set evaluation. Include this flag to evaluate the model on the
  test set.

In addition to running the code, our pre-computed results can be observed by running:

```
python automates/code_summarization/src/scripts/dataset_scores.py <score-file>
```

where `score-file` is one of the pickle files stored at
`/path/to/code-summ-corpus/results/`.

##### Running the summary generation experiment

The natural language summary generation experiment can be run with the
following command:

```
python automates/code_summarization/src/generation.py [-e <amt>] [-b <amt> [-g] [-d] [-t]
```

All of the flags mentioned in the command above have the same definitions as
the commands outlined in the above section dealing with our classification
experiments.

Our generation results can also be verified using our pre-computed results with
the following script:

```
python automates/code_summarization/src/utils/bleu.py <truth-file> <trans-file>
```

where `truth-file` and `trans-file` are text files located at stored at
`/path/to/code-summ-corpus/results/`. Note that the two files should have the
same prefix, the `truth-file` should end with `_truth.txt`, and `trans-file`
should end with `_trans.txt`.
