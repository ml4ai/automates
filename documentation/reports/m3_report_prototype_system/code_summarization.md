### Encoder/decoder generation results
Our experiments with an encoder/decoder model showed that our model was not able to acquire enough signal to adequately generate docstring summarizations for source code. Our results indicated that the model was failing to learn from the data. We decided on the three following tasks that would help increase our models ability to learn from data and allow us to debug what portions of the model may be failing. The first task is to reassess the code/docstring corpus to see if there were unnecessary sources of error in the corpus and to attempt to gather more data. The second task is to reassess the code/docstring embeddings by observing the vocabulary size and determining whether lowering the vocabulary size is possible, and whether it would aid the generation model. The third task is to create a model for a simpler task (classification) that has the same form as the model for our generation task that we can use to assess whether their is enough signal for the generation model to be able to generate docstring summarizations given our dataset. In the following three sections we will outline the progress we have made on these three tasks. Following that we will discuss our plans for the future of the code-summarization portion of the project.

### Progress on code/docstring corpus
The team was able to increase the size of our overall code/docstring corpus by indexing more python packages to look for additional python functions that had PEP-style descriptive docstrings. We were able to index additional python packages from the following lists of packages: the [anaconda distribution](https://docs.anaconda.com/anaconda/packages/py3.6_osx-64/), the [awesome-python](https://github.com/vinta/awesome-python) list, and the list of all available [SciKit packages](http://scikits.appspot.com/scikits). In total we increased the amount of python packages that we are searching for code/docstring pairs to add to our corpus from only 24 to 1132. However, the amount of data we discovered from these packages has only increased from roughly 22,000 examples to roughly 82,000 examples.

### Progress on code/docstring embeddings


### Docstring classification task
##### Random-draw and challenge dataset description

##### Baseline neural model description

##### Initial classification results
