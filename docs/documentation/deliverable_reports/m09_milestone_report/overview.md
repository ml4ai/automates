Link to the [PDF version of this report](ASKE_M09Report_UA-AutoMATES-20190701.pdf).

## Overview

This report summarizes progress towards AutoMATES milestones at the nine month mark, emphasizing changes since the m7 report.

Work this phase has focused on perparations for the September demo, in collaboration with GTRI and Galois.

Highights:

* Program Analysis haindling GOTO statements, representing floating point precision, and handling of some lexical differences between Fortran dialects
* Summary of current DSSAT code coverage (in Program Analysis section); key highlight: of 162,290 lines of source code in DSSAT, PA can now handle 144,370, or 89%.
* Work on the general information source grounding/linking task: how we association source code elements (identifiers), equation terms and concepts expressed in text (both in comments and documentation). We have initial methods for linking some elements, with focus on linking equation terms to document text elements.
* Text Reading progress on extracting variable value unit information from text.
* Equation Reading has full implementation the im2markup model for extracting equation latex from images and has compiled a corpus of 1.1M equation examples. Team now working on data augmentation to improve equation extraction generalization.
* Model Analysis has developed an algorithm for variable value domain constraint propagation, identifying the possible intervals of values that can be computed given the source code representation.

