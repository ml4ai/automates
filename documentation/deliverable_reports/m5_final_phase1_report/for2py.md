### Program Analysis: for2py

The core functionality of `for2py` is that of extracting the syntactic structure of the input code in the form of an *abstract syntax tree* (AST), which is then written out in a form suitable for subsequent analyses.  Idiosyncracies of the Fortran language make it non-trivial and time-consuming to construct a Fortran parser from scratch, while most available Fortran parsers are part of compilers and closely integrated with them, making the extraction of the AST difficult.  The only suitable Fortran parser that we found, and which we use in `for2py`, is an open-source tool `OFP` (Open Fortran Parser).  While its functionality as a Fortran parser fits our needs, `OFP` suffers from some shortcomings, e.g., an inability to handle some legacy constructs and handling a few other constructs in unexpected ways, that require additional effort to work around.

#### Architecture

The architecture of the `for2py` Fortran-to-GrFN translator is shown below.  It is organized as a pipeline that reads in the Fortran source code, transforms it through a succession of intermediate representations, as described below, and writes out the GrFN representation of the code along with associated Python code ("lambdas").

![for2py architecture](https://github.com/ml4ai/automates/blob/m5_phase1_report/documentation/deliverable_reports/m5_final_phase1_report/for2py-architecture.png)


The processing of the input source code proceeds as follows:

* **Preprocessing:** This step processes the input file to work around some legacy Fortran features (Fortran-77) that `OFP` has trouble handling, e.g., continuation lines, comments in certain contexts.
* **Comment processing:** Like most other programming language parsers, `OFP` discards comments.  Since comments play a vital role in AutoMATES, we use a separate processing step to extract comments from the input code for later processing.  For comments associated with particular lines of code, we add special marker statements into the source code that become embedded in the AST.  This allows us to subsequently associate the extracted comments with the corresponding points in the code.
* **AST rectification:** The ASTs produced by `OFP` for some language features have unexpected complexities in their structure that complicate subsequent processing.  This occurs, for example, with derived types (which are akin to C `structs`) and `FORMAT` statements in certain contexts.  To simplify subsequent processing, and also to isolate subsequent processing from such parser-specific idiosyncracies, we transform the ASTs produced by `OFP` to remove such complexities ("rectification").
* **AST transformation:** This step takes the rectified ASTs in XML form and simplifies them by removing irrelevant Fortran-specific details.  It then combines the resulting data structure with the comments extracted from the program so that comments can be correlated with the appropriate program points.  The result is written out as a pickled Python data structure.
* **AST to IR lifter:** The simplified AST resulting from the previous step is then lifted into `for2py`'s internal representation (IR).  As an intermediate step of this process, `for2py` generates a Python program that is behaviorally equivalent to the input code and which can be used to validate the translation.
* **GrFN generation:** The IR constructed in the previous step is mapped to the GrFN specification of the input code together with associated Python functions ("lambdas")



#### Instructions for running components

Many of the components in the pipeline described above can be run as stand-alone programs as described below.

* **Preprocessing:**
    `python preprocessor.py` *infile* *outfile*

* **Comment processing:** 
    `python get_comments.py` *src_file_name*

* **OFP parser:**
    `java fortran.ofp.FrontEnd --class fortran.ofp.XMLPrinter --verbosity 0` *src_file* `>` *ast_file*

* **AST transformation:** 
    `python translate.py -f` *ast_file* `-g` *pickle_file* `-i` *src_file*

* **AST to IR lifter:** 
    `python pyTranslate.py -f` *pickle_file* `-g` *py_file* `-o` *out_file*

* **GrFN generation:** 
    `python genPGM.py -f` *py_file* `-p` *grfn.json* `-l` *lambdas.py* `-o` *out_file*


#### Updates

>TODO: Summary (bullet points) of updates since last report.
