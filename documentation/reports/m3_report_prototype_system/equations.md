# Equation detection and parsing

## ArXiv bulk download

The team has downloaded the complete set of arXiv PDFs their corresponding
source files from Amazon S3 as described
[here](https://arxiv.org/help/bulk_data_s3).

## Preprocessing pipeline

The team has put together a preprocessing pipeline with the purpose of
preparing the data for training the statistical models.

First, we arrange the source files retrieved from arXiv in a directory
structure where the first directory corresponds to the year and month of the
paper submission (e.g. `1810`). Inside, each paper source files are stored in
a directory named after the paper's id (e.g. `1810.04805`).

Then, the file that has the `\documentclass` directive is selected as the main
tex file (see https://arxiv.org/help/faq/mistakes#wrongtex). Once a main tex
file has been selected, the tex source is tokenized and the content of certain
environments are collected together with the environment itself (e.g. the
tokens inside the `begin{equation}` and `\end{equation}` directives, together
with the label `equation`).

From this point, the team has focused on processing the tex code extracted
from `equation` environment and is just collecting the code from other math
environments for later use.

The extracted code is rendered into a standalone equation image and then the
PDF file is scanned using
[template matching](https://docs.opencv.org/4.0.0/df/dfb/group__imgproc__object.html).
The resulting axis-aligned bounding box (AABB) is stored for the subsequent
training of an equation detector.

The team will next work on the preprocessing of the extracted tex tokens for
the removal of superfluous code such as `\label{}` directives, as well as
on expanding user-defined macros.

### Data driven analysis of preamble to inform template design

The team has conducted an analysis on a subset of the arXiv retrieved
sources to inform the design of the templates used to render standalone
equation images. The purpose of this analysis is the identification of
the tex packages more commonly used for the writing of math in academic
papers.

TODO results

## Deploying `im2markup` on UofA HPC

The team has built a
[singularity container](https://www.sylabs.io/guides/3.0/user-guide/)
with the lua and python libraries required to run
[im2markup](https://github.com/harvardnlp/im2markup).
