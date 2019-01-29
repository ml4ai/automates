# Equation detection and parsing

## ArXiv bulk download

The team has downloaded the complete set of arXiv PDFs their corresponding
source files from Amazon S3 as described
[here](https://arxiv.org/help/bulk_data_s3).

## Preprocessing pipeline

The team has put together a preprocessing pipeline with the purpose of
preparing the data for training the statistical models.

First, the source files retrieved from arXiv are arranged in a directory
structure where the first directory corresponds to the year and month of the
paper submission (e.g.,`1810` corresponds to October 2018). 
Inside, each paper's source files are stored in
a directory named after the paper's id (e.g., `1810.04805`).

Then, the file that has the `\documentclass` directive is selected as the main
tex file (see https://arxiv.org/help/faq/mistakes#wrongtex). Once a main tex
file has been selected, the tex source is tokenized and the content of certain
environments are collected together with the environment itself (e.g., the
tokens inside the `begin{equation}` and `\end{equation}` directives, together
with the label `equation`).

Currently, the team is focused on processing the tex code extracted
from the `equation` environment, while still collecting the code from other math
environments for later use.

The extracted code for each equation is rendered into a standalone equation image, and then the
PDF file for the entire paper is scanned for this standalone image using
[template matching](https://docs.opencv.org/4.0.0/df/dfb/group__imgproc__object.html).
The resulting axis-aligned bounding box (AABB) is stored for the subsequent
training of an equation detector.

The team will next work on the preprocessing of the extracted tex tokens to provide
the equation decoder a more consistent input.  At minimum, the preprocessing will include 
the removal of superfluous code such as `\label{}` directives, the normalization of 
certain latex expressions (e.g., arbitrary ordering of super and sub-script in equations), 
and expanding user-defined macros.

### Data driven analysis of preamble to inform template design

The team has conducted an analysis on a sample of 1600 of the arXiv retrieved
sources to inform the design of the templates used to render standalone
equation images. The purpose of this analysis is the identification of
the math environments and tex packages that are most commonly used for 
the writing of math in academic papers.  By knowing which environments and packages
are most common, the team can assemble a template that (a) has broad coverage (i.e., 
can make the most use of the training data) and (b) is minimal (i.e., will be faster 
to run and will have fewer conflictes).

The analysis shows that the most commonly used math environments (in order) are:
`equation`, `align`, and `\[ \]`.  While the team currently handles the `equation`
environment (40% of the equations found), the pipeline will be extended to accomodate
the other two as well.  In terms of the preamble packages related to math rendering, 
both `amsmath` and `amssymb` occurred in over 70% of the main files, and the next most
common package (`amsfonts` occurred in only 35% of the main files).  Accordingly,
the initial template for rendering the standalone equations contains those two most
prevalent packages for now, with the option to extend as needed in the future.

## Deploying `im2markup` on UofA HPC

The team has built a
[singularity container](https://www.sylabs.io/guides/3.0/user-guide/)
with the lua and python libraries required to run
[im2markup](https://github.com/harvardnlp/im2markup).  This will allow for rapid development
of the equation decoding system.
