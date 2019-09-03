In addition to extracting information from source code, the AutoMATES
team will be automatically extracting complementary scientific
information from academic papers, including the description of
model-relevant equations and the variables that comprise them, along
with the information required for the sensitivity analysis of the
models of interest in this project (such as variable domain types,
ranges, and default values, etc.).  Once extracted, this information
will be grounded, or linked, to the [model components extracted from
the original source code](#2-program-analysis).

Supporting code for this pipeline will be implemented in the
[AutoMATES](https://github.com/ml4ai/automates) repostory.

### Automatic reading of scientific discourse expressed in natural language

The scientific papers that describe the models of interest will be read
to extract two different types of information: (1) contextual
information relevant to the models of interest, and (2) specific
descriptions of equations and variables, as well as any discussion of the
relations they have with each other.

#### Extracting context

There is a wide range of contextual information expressed in
scientific descriptions of models, including ranges and units for
variables, confidence scores such as *p*-values, and overall context
required for analysis of the executable models (variable domain types,
default values, etc.). In order to extract this information, the
papers, which are typically found in PDF form, will be converted to
text. The team will evaluate several off-the-shelf tools for this
conversion and select the one that performs the best for the intended
purpose. Potential tools include (but are not necessarily limited to)
[GROBID](https://github.com/kermitt2/grobid), [Science
Parse](https://github.com/allenai/science-parse), and [Science Parse
version 2](https://github.com/allenai/spv2).

As the PDF-to-text conversion process is always noisy, the text will
then be filtered to remove excessively noisy text (e.g., poorly
converted tables) using common sense heuristics (e.g., sentence length
and occurrence of certain special characters). Finally, the text will be [syntactically parsed](https://github.com/clulab/processors) and processed with 
[grobid quantities](https://github.com/kermitt2/grobid-quantities), which 
identifies and normalizes text mentions of measurements.  


After preprocessing, the contextual information will be extracted
through the use of
[Odin](http://www.lrec-conf.org/proceedings/lrec2016/pdf/32_Paper.pdf)
rule grammars, which can be constructed and refined quickly.  Odin
grammars have proven to be reliable, robust, and efficient for diverse
reading at scale in both the Big Mechanism program (with the
[Reach](https://academic.oup.com/database/article/2018/1/bay098/5107029)
system) and the World Modeler's program (with the
[Eidos](https://github.com/clulab/eidos/) system).  The flexibility of
Odin's extraction engine allows it to easily ingest the normalized
measurements mentioned above along with the surface form and the dependency 
syntax, such that all representations can be used in the rule grammars during 
extraction.

#### Extracting equation and variable descriptions

In addition to contextual information, the team will also focus on
extracting the descriptions of model-relevant equations and their
variables found in the scientific literature, which typically occur in
the immediate vicinity of the presentation of the equations themselves.
However, during the conversion from PDF to text, information about the
original _location_ of a given span of text is lost. For this reason, in
order to extract these descriptions, the team will first implement a
component that identifies the regions of interest in the academic
documents.

Specifically, using the [axis-aligned bounding box found for a given
equation](#equation-detection), the team will expand it to get the text
surrounding the equation.  Additionally, the PDF can be converted to
text in layout-preserving mode (using [Poppler's
pdf2text](https://poppler.freedesktop.org/)), which will allow the team
to locate the equation identifier and therefore the text around it,
as well as extract the entities and relations required for the grounding
the models built by other components of our system.

Once the region surrounding the equation is identified, Odin rules
will likewise be used on the text within that region to extract
descriptions of the equation and the variables it contains, as well as
any descriptions relations between variables.

### Grounding

After extraction, it will be necessary to ground the variables and
equations.  There are two distinct types (or directions) of grounding
that will be necessary.  The first is to associate a description to a
variable, and the other is to associate two variables (one extracted
from source code and another from text) with each other based on their
descriptions and other information such as model structure (e.g., if
they are both in a denominator, etc.).

The first type of grounding will link the variables and equations
found in the scientific papers with their descriptions.  This is seen
in the following paper excerpt that shows an example of an equation
and its description:

<p align="center">
<img src="figs/reynolds_number_equation_screenshot.png" width="90%">
</p>

Here, each of the variables in the equation (e.g., `L` and `V`) will
be linked to their extracted descriptions (`characteristic length`
and `velocity scales`).  Additionally, the entire equation will be
linked to its description (`Reynolds Number`).  Any other instances of
these variables or equations in the text document will also be linked,
under the assumption of [one sense per
discourse](http://aclweb.org/anthology/H92-1045).  Likewise, variables
occurring in the source code will be linked with any comments that
describe them.

The variables and equations from each of these sources (code and text)
will then be matched to each other, by generating a mapping from
equation variable to code variable using their attached descriptions
to inform the alignment process.  For this, the team will initially
use the domain ontology grounding component of
[Eidos](https://github.com/clulab/eidos) that is used to align
high-level concepts (such as _rainfall_) with mid- and low-level
indicators and variables (such as
`Average_precipitation_in_depth_(mm_per_year)`).  This component is
based on word similarity, as determined using pretrained word
embeddings, and will be extended as necessary to adapt it to this
particular use case.
