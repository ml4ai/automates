## Text Reading

### Architecture

To contextualize the models lifted from source code, we have implemented a
machine reading system that extracts model information from two sources: (_a_)
the scientific papers and technical documents that describe a model of interest
(from which we extract the variables, the definitions for those variables, and
the parameter settings for the variables); and (_b_) the comments from the
Fortran source code (from which we can extract the variables, variable
definitions, and potentially the units).

![Architecture of the text reading pipeline](figs/textrdg-architecture.png)

**Figure 9**: Architecture of the text reading pipeline.

For paper text extraction, we use a [pre-processing
pipeline](#natural-language-data-preprocessing) that converts PDFs to text,
parses the text, and extracts measurements. A set of [rule
grammars](#rule-based-extraction-framework) then extract variables, their
descriptions, and their values. For the source code comment extraction, we also
use rule grammars to extract the variables and descriptions. The text variables
are aligned with their corresponding comment variables using lexical semantics to
provide richer context for the [CodeExplorer webapp](#codeexplorer) as well as
to inform analyses performed in downstream components (e.g., model Sensitivity
Analysis).

Detailed instructions on how to run this pipeline are provided
[below](#instructions-for-running-text-reading-components).

### Natural language data preprocessing

The first stage in the text reading pipeline consists of processing the source
documents into a format that can be processed automatically. As the documents
are primarily in PDF format, this requires a PDF-to-text conversion. The team
evaluated several tools on the specific types of documents that are used here
(i.e., scientific papers) and in the end chose to use [Science
Parse](https://github.com/allenai/science-parse) for both its quick processing
of texts as well as the fact that it does a good job handling section divisions
and Greek letters. Science Parse was then integrated into the text reading
pipeline via a Docker container such that it can be run offline (as a
preprocessing step) or online during the extraction.

As the PDF-to-text conversion process is always noisy, the text is then
filtered to remove excessively noisy text (e.g., poorly converted tables) using
common sense heuristics (e.g., sentence length). This filtering is modular, and
can be developed further or replaced with more complex approaches.

After filtering, the text is [syntactically
parsed](https://github.com/clulab/processors) and processed with
[grobid-quantities](https://github.com/kermitt2/grobid-quantities), an
open-source tool which finds and normalizes quantities and their units, and
even detects the type of the quantities, e.g., _mass_. The tool finds both
single quantities and intervals, with differing degrees of accuracy. The
grobid-quantities server is run through Docker and the AutoMATES extraction
system converts the extractions into mentions for use in later rules (i.e., the
team's extraction rules can look for a previously found quantity and attach it
to a variable). While grobid-quantities has allowed the team to begin
extracting model information more quickly, there are limitations to the tool,
such as unreliable handling of Unicode and inconsistent intervals. For this
reason, the extraction of intervals has been ported into [Odin (rule-based
extraction)](#rule-based-extraction-framework), where the team is using syntax
to identify intervals and attach them to variables.

### Rule-based extraction frameworks

For extracting model information (e.g., variables, their descriptions, values,
etc.) from free text and comments, the team implemented a light-weight
information extraction framework for use in the ASKE program. The system
incorporates elements of the machine reader developed for the World Modelers
program, [Eidos](https://github.com/clulab/eidos) (e.g., the development webapp
for visualizing extractions, entity finders based on syntax and the results of
grobid-quantities, and the expansion of entities (Hahn-Powell et al., 2017)
that participate in relevant events) along with new
[Odin](http://clulab.cs.arizona.edu/papers/lrec2016-odin.PDF) grammars
(Valenzuela-Escárcega et al., 2016) for identifying, quantifying, and defining
variables, as shown in the screenshot of the development webapp in Figure 10.

![Screenshot of ASKE text reading webapp for rapid rule development](figs/extractions.png)

**Figure 10:** Screenshot of ASKE text reading webapp for rapid rule development.

Odin grammars have proven to be reliable, robust, and efficient for diverse
reading at scale in both the DARPA Big Mechanism program (with the
[Reach](https://academic.oup.com/database/article/2018/1/bay098/5107029)
system) and the DARPA World Modelers program (with the
[Eidos](https://github.com/clulab/eidos/) system). The flexibility of Odin's
extraction engine allows it to easily ingest the normalized measurements from
grobid-quantities along with the surface form and the dependency syntax of the
text, such that all representations can be used in the rule grammars during
extraction.

To promote rapid grammar development, the team is using test-driven
development. That is, the team has created a framework for writing unit tests
representing ideal extraction coverage and is adding rules to continue to
increase the number of tests that are passed. This approach allows for quickly
increasing rule coverage (i.e., we are writing more rules as we continue to
analyze the data and the outputs from the text reading system) while ensuring
that previous results are maintained.  Currently, there are 83 tests written to
test the extraction of variables, definitions, and setting of parameter values
from text and comments, of which 45 pass.

#### Summary of extraction unit tests

| Type of Extraction   | Number of Tests | Number Passing |
| -------------------- | --------------- | -------------- |
| Comment defintions   | 6               | 6              |
| Parameter Setting    | 12              | 6              |
| Variables            | 30              | 17             |
| Free text defintions | 35              | 16             |
| TOTAL                | 83              | 45             |

Unsurprisingly, fewer of the tests for free text (i.e., the scientific papers)
pass, as there is much more linguistic variety in the way variables and their
definitions or descriptions are written. Moving forward, the team will continue
to develop the grammars to increase recall, as well as performing a more formal
evaluation of the precision.

For paper reading, we currently have several small sets of rules written for
extracting entities (eight rules), definitions (four rules), and parameter
settings (eight rules). The rules for parameter settings extract both values
and value intervals/ranges, as shown in Figure 11.

![Example of extraction of parameter values and ranges from free
text.](figs/paramSettingVisualization.png)

**Figure 11:** Example of extraction of paramter values and ranges from free text.

#### Extraction from comments

For comment extraction, we currently consider all of the comments from a given
source file, though in the future we will implement the ability to query
ever-widening program scopes to retrieve sections of comments which are most
relevant to a given GrFN variable. We then use regular expressions to parse the
comment lines, which cannot be straightforwardly be processed using standard
tools because the sentence boundaries are not easily determinable, and even if
segmented, the comments are not true sentences. Then, we locate instances of
the model variables which are retrieved from the GrFN JSON by using string
matching. Finally, we use surface rules to extract the corresponding
descriptions.

Since there is less variability in the way comments are written than text from scientific papers, there were only two rules necessary for comment reading---one for extracting the variable and one for extracting the definition for the variable.

#### Future work

We plan to work towards increasing the _recall_ of free text extractions by
writing rules to extract the target concepts from a wider variety of both
syntactic and semantic contexts, increasing the _precision_ by constraining the
rules in such a way as to avoid capturing irrelevant information, and
templatizing the rules wherever possible to make them easier to maintain.
Additionally, we will gradually extract additional relation types (e.g.,
_precondition_) that are determined to be useful by the downstream consumers —
that is, we will continue to develop the extractions to better facilitate Model
Comparison and Sensitivity Analysis.

### Alignment

We have implemented an initial variable mention alignment module, based on the
lexical semantic approach used to ground concepts in the Eidos system.
Variables are first retrieved from the GrFN JSON and then their comment
descriptions are extracted [as described above](#extraction-from-comments).
Then, each of these variables is aligned with variables (and their defintions)
from free text. The alignment is based on comparing _word embeddings_ from the
words in the defintions. Formally, each of the vector embeddings for the words
in the description of a GrFN variable, $$v_G$$, are compared (using [cosine
similarity](https://en.wikipedia.org/wiki/Cosine_similarity)) with each of the
embeddings for the words in the definition of a text variable, $$v_t$$. The
score for the alignment between the variables, $$S(v_G, v_t)$$, is the sum of
the average vector similarity and the maximum vector similarity, for a score
which ranges between $$[-2.0, 2.0]$$. The intuition is that the alignment is
based on the overall similarity as well as the single best semantic match. This
approach is fairly naive, but turns out to be robust. The team will continue to
develop this approach as the program continues, ideally by making use of
external taxonomies which contain additional information about the variables
and also the variable type (i.e., int, string, etc.) and units found in the
text and comments. The final alignments are output to the GrFN JSON for
downstream use.


### Instructions for running text reading components

We have separate README files that provide instructions for running the
individual components of the text reading pipeline:

- [Development webapp](readmes/README_development_webapp) for visualizing
  the extractions
- [ExtractAndAlign](readmes/README_extract_and_align)
  entrypoint, for extracting model information from free text and comments and
  generating and exporting alignments. This is the primary pipeline for the
  text reading module.


### Updates

The team has made progess in several areas since the last report. Here we
summarize the new additions, which are described in much more detail in the
sections above.

- **Alignment**: Since the last report, the team has added the Alignment
  component descibed above to align the variables from the source, the mentions
  of these variables in the comments, and the corresponding variables in the
  free text model descriptions.
- **Import and export in GrFN JSON format**: To facilitate the extraction of
  variables and descriptions from comments as well as to provide the aligment
  information to downstream components, the team has added code to parse GrFN
  JSON files and generate new versions with the text-extracted context
  associated with GrFN variables.
- **Reading of comments**: The team added code to select relevant lines from
  the source code comments and tokenize them. Additionally, a small number of
  new rules were developed to extract variables and descriptions from the
  comment text.
