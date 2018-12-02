## AutoMATES Architecture Overview

<img src="figs/20181129_architecture_numbered.png" width="100%" />

The AutoMATES architecture is summarized in the figure above.  

On the far left are the two information sources input to AutoMATES: source text from documents that describe scientific models, including equations, and source code implementing scientific models, which contains both program instructions and comments.

Along the top of the figure are four headings that describe the general category of processing being conducted by the architecture:
1. *Extraction* of information out of the data sources.
2. *Grounding* extracted information by linking between information types and connecting to scientific domain ontologies.
3. *Comparison* of models by analyzing structural and functional similarities and differences.
4. *Augmentation* of models by composing models or their components, choosing between component appropriate for a task,and execution.

The following sections in the remainder of this report describe in detail the components of the architecture.  The numbers in the architecture summary figure correspond to the number of the section providing details about the component.
