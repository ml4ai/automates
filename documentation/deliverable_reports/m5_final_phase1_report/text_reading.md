### Text Reading

#### Architecture

>TODO: Description of the current state of the text reading architecture.
Possibly include a figure (architecture diagram)?

- pdf2text
- extracting quantities
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
