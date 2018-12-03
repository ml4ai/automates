---
title: About
---

There exist today state-of-the-art computational models that can provide highly
accurate predictions about complex phenomena such as crop growth and weather
patterns. However, certain phenomena, such as food insecurity, involve a host of
factors that cannot be modeled by any single one of these models, but which
instead require the integration of multiple models.

To truly integrate these computational models, it is necessary to 'lift' them to
a common representation that is (i) agnostic to the software implementation,
(ii) semantically rich enough to represent the implicit domain knowledge in the
models, and (iii) connected to the domain literature.


The AutoMATES project aims to build technology to construct and curate
semantically-rich representations of scientific models by integrating three
different sources of information:

- natural language descriptions of models in publications and other technical documentation,
- the equations contained in these documents, and
- the software the implements these models.


In the figure below, a dynamical model describing the biophysical variable Leaf
Area Index (LAI) is described using text, equations, and software (left half of
the figure). The network on the right half is an aspirational representation of
the model as a Bayes network. Although this example is hand-crafted, our end
goal is to be able to automatically assemble models with this level of semantic
richness.

![confluence_example](confluence_example.png)

This work will dramatically advance the state-of-the-art in automated model
curation and integration, enabling scientists and analysts to understand complex
mechanisms that span multiple domains. By exposing the implicit domain knowledge
baked into computational models, this effort will enable automated model
composition and reasoning in context to directly support the development of
‘third wave’ artificial intelligence.

## Software

The machine reading of the scientific papers is done using a tool built upon
[processors](https://github.com/clulab/processors), the parsing of equations in
PDFs of scientific papers is done using the
[equation parser module](equation_extraction), and the program
analysis and model assembly is performed by
[Delphi](https://github.com/ml4ai/delphi).
