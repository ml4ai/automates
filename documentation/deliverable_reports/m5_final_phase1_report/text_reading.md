### Text Reading

#### Architecture

>TODO: Description of the current state of the text reading architecture.
- TODO architecture
- Possibly include a figure (architecture diagram)?

- High level and include Odin
- processing text from scientific documents and comments
- aligning based on string edit dist and the lexical semantics of the descriptions
- the alignments are provided to downstream components

### Data formatting
The first stage in the text reading pipeline consists of processing the source 
documents into a format that can be processed automatically.  As the documents
are primarily in pdf format, this requires a PDF-to-text conversion.  
The team evaluated several tools on the specific types of documents that are used 
here (i.e., scientific papers) and in the end chose to use [science
parse](https://github.com/allenai/science-parse) for both its quick
processing of texts as well as the fact that it does a good job handling section
divisions and greek letters. Science parse was then integrated
into the text reading pipeline via a Docker container such that it can be run
offline (as a preprocessing step) or online during the extraction.

As the PDF-to-text conversion process is always noisy, the text is
then filtered to remove excessively noisy text (e.g., poorly
converted tables) using common sense heuristics (e.g., sentence length).  This
filtering is modular, and can be developed further or replaced with more complex 
approaches. 

### Data pre-processing
After filtering, the text is 
[syntactically parsed](https://github.com/clulab/processors) and processed with
[grobid quantities](https://github.com/kermitt2/grobid-quantities), 
an open-source tool which finds and normalizes quantities and their units, and even detects
the type of the quantities, e.g., _mass_.  The tool finds both single
quantities and intervals, with differing degrees of accuracy.  The
grobid-quantities server is run through Docker and the AutoMATES
extraction system converts the extractions into mentions for use in
later rules (i.e., the team's extraction rules can look for a previously
found quantity and attach it to a variable).  While grobid-quantities
has allowed the team to begin extracting model information more quickly,
there are limitations to the tool, such as unreliable handling of unicode
and inconsistent intervals.  
For this reason, the extraction of intervals has been ported into Odin, where the
team using syntax to identify intervals and attach them to variables. 
- TODO (MASHA+ANDREW): example from webapp?


### Rule-based extraction framework

In terms of extraction, the team has begun implementing a light-weight
information extraction framework for use in the ASKE program.  The
system incorporates elements of [Eidos](https://github.com/clulab/eidos)
(e.g., the webapp for visualizing extractions, entity finders based on
syntax and the results of grobid-quantities, and the expansion of
entities that participate in relevant events) along with new
[Odin](http://clulab.cs.arizona.edu/papers/lrec2016-odin.pdf) grammars
for identifying, quantifying, and defining variables, as shown here: 

![A screenshot of the web-based visualizer showing the results of
the rule-based extraction framework.](figs/extractions.png)

**Figure 3:** A screenshot of the web-based visualizer showing the results of the rule-based extraction framework.

This project is fully open-source and has already been utilized and
contributed to by the Georgia Tech ASKE team.

To promote rapid grammar development, the team has developed a framework
for writing unit tests to assess the extraction coverage.  Currently, 
there are 77 tests written to test the extraction of variables, 
definitions, and setting of parameter values, of which 16 pass. 
This test-driven approach (in which we first write the tests based on 
the desired functionality and then work to ensure they pass) will allow 
for quickly increasing rule coverage while ensuring that previous results 
are maintained. 

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

Once the region surrounding the equation is identified, Odin rules
will likewise be used on the text within that region to extract
descriptions of the equation and the variables it contains, as well as
any descriptions relations between variables.

- reading from papers
    - variables and definitions
    - values and ranges (WIP)
        - grobid unreliable at intervals
- reading from comments
    - definitions of variables represented in GrFN
    - alignment (WIP)
        - lexical semantics of definitions
        - variable name itself
- exporting definitions from text (with alignment) to GrFN
- webapp display

#### Instructions for running components

>TODO: Describe how each individual component of the equation pipeline works, so someone could train/run if desired. E.g., could describe how to launch the TR-Odin component webapp for rule authoring.

- development webapp
- extract and align
- extract and export
- how to launch (docker compose, etc)
    - preprocessing of pdf

#### Updates

>TODO: Summary (bullet points) of updates since last report.

- alignment
- export into json
- reading of comments