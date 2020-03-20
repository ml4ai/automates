## Code Summarization

During this phase, the team began exploration of an encoder/decoder neural network model for code summarization generation. Initial results demonstrated that the model was
not able to acquire enough signal to adequately generate docstring
summarizations for source code. In response, the team developed the following three tasks to improve the model. 

- The first task involved reassessing the quality of the code/docstring training corpus to see if there are avoidable sources of error in the corpus and to attempt to gather more data. 

- The second task involved trying different approaches to the code/docstring embeddings by investigating the vocabulary size (too may vocabulary items can lead to data sparsity) and possible methods for reducing the vocabulary.

- The third task involved creating a model for a simpler task (classification) that has
the same form as the model for our generation task but that we can used to
directly assess the embedding representation quality.

In the following three sections we will outline the progress we have made on
these three tasks.

### Progress on code/docstring corpus

The team was able to increase the size of our overall code/docstring
corpus by indexing more Python packages to identify additional Python
functions that have PEP-style descriptive docstrings. We were able to
index additional Python packages from the following lists of packages:
the [anaconda
distribution](https://docs.anaconda.com/anaconda/packages/py3.6_osx-64/),
the [awesome-python](https://github.com/vinta/awesome-python) list, and
the list of all available [SciKit
packages](http://scikits.appspot.com/scikits). In total, we increased the
amount of Python packages that we are searching for code/docstring pairs from 24 to 1132. 

From these packages, we have extracted code/docstring pairs, increasing our corpus from approximately 22,000 examples to approximately 82,000. The following graphic summarizes the styles of code-bases and their relative contributions to the
code/docstring pairs to our corpus.

---

![Graphical view of the amount of usable code/docstring
pairs each python module has added to our code-summarization corpus
(only the 25 modules with the largest amount of usable pairs are shown)
Modules are color-coded according to the type of code most likely to be
found in the module.](figs/module_corpus_contributions.png)

**Figure 8:** Graphical view of the amount of usable code/docstring
pairs each python module has added to our code-summarization corpus
(only the 25 modules with the largest amount of usable pairs are shown)
Modules are color-coded according to the type of code most likely to be
found in the module.

---

### Progress on code embeddings

Neural network model performance has been found to strongly depend on the quality of the embedding model used to represent the data.
One of the biggest struggles for any embedding is to ensure that enough
examples are present for every token you wish to embed. Without a large
number of examples the embedding space cannot create meaningful
embeddings for corresponding tokens. In the case of creating embeddings
for code, it is likely the case that the names of functions are going to
be some of the most important tokens to embed, and unfortunately these are also
the most infrequent if each unique name is treated as a single token. From our
original dataset of 22,000 examples we had roughly 53,000 unique tokens
in the code portion of our corpus. The vast majority of these were
function or variable names that occurred fewer than five times each, not
nearly enough to be able to establish useful embeddings that capture the
type of semantic information carried in function or variable names.

To address this issue, we split function and variable
names into sub-components using `snake_case` and `camelCase` rules, to extract the repeated mentions of name that occur as parts of function and variable names.
Some examples of the tokenized forms of function names found in our
corpus before and after the transformation are provided in the following
table.

| Original tokenization       | Split-name tokenization                   |
| ---                         | ---                                       |
| `compute_ldap_message_size` | `<BoN> compute ldap message size <EoN>`   |
| `getComponentByPosition`    | `<BoN> get Component By Position <EoN>`   |
| `fromOpenSSLCipherString`   | `<BoN> from Open SSL Cipher String <EoN>` |
| `fromISO8601`               | `<BoN> from ISO 8601 <EoN>`               |

Splitting functions/variable names in this way decreased our code vocabulary size from
roughly 53,000 to roughly 16,000 unique tokens while also lowering the
number of tokens that appear fewer than five times from roughly 35,000
to roughly 5,000.

### Docstring classification task

One of the difficulties with generation tasks is being able to tell
whether your model has enough signal from the data to be able to
generate affectively. 

In order to evaluate whether our dataset provides enough signal for our generation task, we have designed a separate classification task in which the classifier is presented with a code and docstring pair and must predict whether the docstring describes the code, which we approximate by using the docstrings associated with code blocks in our corpus. In the following sections we describe the the classifier, present the two classification datasets we are using, present some preliminary classification results, and discuss the next steps for using these methods to improve the code summary generation model.

##### Baseline neural model description

Our initial classification model is a simplification from the model we originally planned to use for generation. The model first embeds a code sequence using our pretrained code embeddings and embeds a docstring using our pretrained docstring embeddings. The two embedded sequences are each fed into their own respective [Bi-LSTM
recurrent
network](https://pdfs.semanticscholar.org/4b80/89bc9b49f84de43acc2eb8900035f7d492b2.pdf).
The final hidden state outputs from these networks are then concatenated and fed into a deep feed-forward neural network that produces a binary classification of whether the docstring is correctly paired with the provided function.

Our rationale for simplifying the model used for classification is that we are currently testing to see if our data is providing enough signal to aid in classification. Once we verify that we do have enough signal to allow for decent classification results, we will increase the models complexity. It is important to note that since the main purpose of the classification model is to test the fitness of our data for generation, we cannot add any docstring specific information to the classification model, since such information would not be present during docstring generation.

##### Random-draw and challenge dataset description

We have constructed two different datasets from our code/docstring corpus that we will use to test the classification model. 
The corpus itself only provides positive examples of docstrings paired with code blocks, so in order to create negative examples, we use a common practice in NLP known as _negative sampling_ to match code blocks with docstrings other than their correct docstring. This creates instances for our classifier to correctly label as mismatched pairs. We have done this with both of our datasets. 

For our first dataset, we use uniform random sampling to select our negative examples. We named this the "random-draw" dataset. We anticipate that this dataset will be easier to obtain good performance as uniform random sampling is likely to pair docstrings with code that is completely unrelated. This dataset is used for the earliest phases of experimentation with our classifier as we are expected to have better chance of training success. Once we determine that our classifier can do reasonably well on the random-draw dataset we will move on to testing our model on our second dataset.

The second dataset uses lexical overlap between the true docstring for a code block and the other candidate docstrings to select a candidate that has the highest lexical overlap with the true docstring (i.e., shares many of the same terms), but is not the correct pairing. This is called the "challenge" dataset, as now the "mismatch" pairings are much more likely to be close but still not correct. This allows us to rigorously test our classifier's ability to correctly identify whether a code/docstring pair is mismatched. To build the dataset, we use [Apache lucene](http://lucene.apache.org/) to index and query our set of docstrings. The following table shows five docstrings with their negative example docstring of highest lexical overlap is provided in the table below.

| Module paths <br> (source, negative)                     | Source docstring                                                                         | Best negative example                                                                                              |
| -------------                                            | -------------                                                                            | ------------                                                                                                       |
| `kubernetes.client.api`<br>`tabpy.client.rest`           | Builds a JSON POST object                                                                | Issues a POST request to the URL with the data specified . Returns an object that is parsed from the response JSON |
| `sympy.ntheory.multinomial`<br>`statsmodels.iolib.table` | Return a list of binomial coefficients as rows of the Pascal's triangle                  | Return list of Row , the raw data as rows of cells                                                                 |
| `matplotlib.image`<br>`PIL.image`                        | Set the grid for the pixel centers , and the pixel values                                | Gets the the minimum and maximum pixel values for each band in the image                                           |
| `mxnet.model`<br>`tensorflow.engine.training`            | Run the model given an input and calculate the score as assessed by an evaluation metric | Sets the metric attributes on the model for the given output                                                       |
| `twisted.internet.tcp`<br>`gevent.server`                | Create and bind my socket , and begin listening on it                                    | A shortcut to create a TCP socket , bind it and put it into listening state                                        |

##### Initial classification results

We have trained and evaluated our baseline model on the random-draw dataset that was
generated by our original corpus (22,000 pairs). After processing over our training set for 35 epochs, our validation set accuracy was 80%, a result that we are very excited about!

##### Next steps

Now that we have increased our corpus size and created our challenge dataset, our immediate next task is to re-evaluate our baseline model on both the random-draw dataset and challenge dataset to see how the changes to our code/docstring corpus affect our performance on our two datasets.

Pending encouraging results on the above experiments, we will begin increasing the complexity of the model by adding character embeddings for the code/docstring tokens. We also plan to add attention layers to the LSTM output from the code and docstring LSTMs that add attention on the alternate sequence respectively. If the results from the above experiments are not as good as we hoped then we will also investigate adding more docstring data to our docstring embeddings from large online documenation repositories such as
[ReadtheDocs](https://readthedocs.org/) to improve the signal from our
docstring sequences.
