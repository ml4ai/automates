## Text Reading

### Converting PDF to text

As discussed in the previous report, the first task required to perform
automated text reading and information extraction was the conversion of
the source documents from PDF to text. This phase the team evaluated several tools on
the specific types of documents that are used here (i.e., scientific
papers) and in the end the team chose to use [science
parse](https://github.com/allenai/science-parse) for both its quick
processing of texts as well as the fact that it does a good job handling section
divisions and greek letters. The team integrated science parse
into the text reading pipeline via a Docker container such that it can be run
offline (as a preprocessing step) or online during the extraction.

### Extracting quantities

The team is also utilzing another open-source tool,
[grobid-quantities](https://github.com/kermitt2/grobid-quantities),
which can find and normalize quantities and their units, and even detect
the type of the quantities, e.g., _mass_.  The tool finds both single
quantities and intervals, with differing degrees of accuracy.  The
grobid-quantities server is run through Docker and the AutoMATES
extraction system converts the extractions into mentions for use in
later rules (i.e., the team's extraction rules can look for a previously
found quantity and attach it to a variable).  While grobid-quantities
has allowed the team to begin extracting model information more quickly,
there are limitations to the tool, such as unreliable handling of unicode
and inconsistent intervals.  The team has opened several issues on the
Github page for grobid-quanities and will continue to do so.  If
nesessary, the extraction of quantities may be moved into the Odin
grammars for full control.

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

### Next Steps

The immediate next steps for machine reading are to expand the coverage
of the rules for natural language text and then to begin extracting
information about variables from source code comments.  The team will
then create an end-to-end alignment tool to map variables found in code
to the corresponding variable described in natural language.
