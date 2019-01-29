### Encoder/decoder generation results
Our experiments with an encoder/decoder model showed that our model was not able to acquire enough signal to adequately generate docstring summarizations for source code. Our results indicated that the model was failing to learn from the data. We decided on the three following tasks that would help increase our models ability to learn from data and allow us to debug what portions of the model may be failing. The first task is to reassess the code/docstring corpus to see if there were unnecessary sources of error in the corpus and to attempt to gather more data. The second task is to reassess the code/docstring embeddings by observing the vocabulary size and determining whether lowering the vocabulary size is possible, and whether it would aid the generation model. The third task is to create a model for a simpler task (classification) that has the same form as the model for our generation task that we can use to assess whether their is enough signal for the generation model to be able to generate docstring summarizations given our dataset. In the following three sections we will outline the progress we have made on these three tasks. Following that we will discuss our plans for the future of the code-summarization portion of the project.

### Progress on code/docstring corpus

### Progress on code/docstring embeddings

### Docstring classification task
##### Beginning and challenge dataset description

##### Baseline neural model description

##### Initial classification results

### Next steps
