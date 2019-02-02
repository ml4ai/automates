Link to the [PDF version of this report](ASKE_M3Report_UA-AutoMATES-20190201.pdf).

## Overview

In this report the AutoMATES team describes the development work done in the past two months on the AutoMATES prototype system. No changes have been made to the overall architecture design, but significant progress has been made in each of the architecture components introduced in the [Month 1 Report](https://ml4ai.github.io/automates/documentation/reports/m1_architecture_report/). We are on track for successfully achieving our Phase 1 goals for the prototype.

Among the highlights for this phase, detailed in the sections below, are the following:

- Deployment of a demonstration web application of the program analysis-to-function network translation translation.
- Extension of the GrFN representation to represent namespaces in identifiers, for handling multi-file and multi-module systems.
- Extensions of the Fortran program analysis module for handling Fortran I/O, Modules, open-ended loops, and arrays.
- Development of the text reading pipeline for converting PDFs to text, extracting quantities and their domains, and a start to developing grammars for extracting variables and associating them with values.
- Development of the equation detection and parsing pipeline as well as collecting the enormous arXiv PDF and TeX source corpus.
- Development of an algorithm to identify structural overlap between two models, through the identification of the Forward Influence Blanket.
- Improving the code summarization training corpus by expanding it dramatically, as well as progress in improving the embedding model for code summary generation.

All code supporting the contributions reported here are available in the [AutoMATES](https://github.com/ml4ai/automates) and [Delphi](https://github.com/ml4ai/delphi/) Github repositories.

