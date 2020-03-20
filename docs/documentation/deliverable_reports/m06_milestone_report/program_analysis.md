## Program Analysis

### Refactoring of front-end:

The focus of work in the past month was on refactoring the “Fortran code -> XML AST -> Python Code” generation process. The refactoring was done in order address issues with the Open Fortran Parser (OFP) AST XML generation that impacted aspects of `translate.py` and `pyTranslate.py` (inefficiency and inconsistencies). The new program `rectify.py` fixes these issues, relieving `translate.py` from having to handle variations in OFP-derived AST representaiton, and focus on generating the pickle file for `pyTranslate.py`. `rectify.py` reduces size of the generated AST XML by 30% to 40% comared to the original XML. For example, the original `PETASCE_markup.xml` is 4,177 lines whereas the new XML is only 2,858 lines. This also speeds up AST processing, reducing the number of special cases required.

### Enhancement of GrFN Specifications and added support for new FORTRAN language features in GrFN

- Continued progress in generating GrFN specification and associated lambda files; this includes abstracting the multi-module structure of the original FORTRAN code into a multi-file GrFN JSON data structure. This phase we developed a strategy for representing modules and this is being implemented in the GrFN spec.
- The Python-to-GrFN converter now handles multi-module files more elegantly with a separate GrFN and lambda file for each FORTRAN module.
- Began refactoring and cleanup of the code-base of the Python-to-GrFN converter. This will allow for more seamless integration of newer FORTRAN language features to the GrFN JSON and lambda file.
- Laid groundwork for the automatic support for inline comments. This will not necessarily be integrated in the GrFN file and might be provided through other means as required.
- Started integration of [PyTorch](https://pytorch.org/) with the automatically generated lambda files. This integration permits much faster code execution.
- Continued discussion and brainstorming about how arrays and multidimensional data structures can be represented in GrFN among other features such as `DELETE`, `SAVE` and `GOTO`.