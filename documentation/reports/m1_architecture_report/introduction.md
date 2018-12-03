## AutoMATES Architecture Overview

<img src="figs/20181129_architecture_numbered.png" width="100%" />

The AutoMATES architecture is summarized in the figure above.  

On the far left of the figure are the two information sources input to AutoMATES: source text from documents that describe scientific models, including equations, and source code implementing scientific models, which contain both program instructions and comments.

Along the top of the figure are four headings (grey text) that describe the general type of processing being done by Automates:
1. *Extraction* of information from the input data sources (text and source code).
2. *Grounding* extracted information by linking between information types (text, equations and source code) and connecting identified terms to scientific domain ontologies.
3. *Comparison* of models by analyzing structural and functional (sensitivity) similarities and differences.
4. *Augmentation* of models by selection of model components appropriate for a task, composing model components, and model execution; AutoMATES produces executable model components (as dynamic Bayesian networks) and provides results of Comparison, but in the ASKE program selection and composition will be done manually by humans.

Extraction and Grounding are performed by three interacting pipelines: Program Analysis, Machine Reading and Equation Reading. 
1. The *Program Analysis* pipeline extracts program source code and associated comments and performs an analysis that identifies variables and the functional relationships between them, as determined by program control flow and expressions. This results in a *Function Network* representation of the variable relationships paired with modular functions that compute the variable states (*Lambdas*). Within the ASKE program, the AutoMATES Program Analysis pipeline will focus on extraction and analysis of Fortran source code. Additional language processing pipelines can be modularly added in the future.
2. The *Machine Reading* pipeline processes text from papers and other documents (input as PDFs) describing scientific models as well as input comments associated with source code. This pipeline extracts contextual information about models models, including identifying mentions of physical variables and grounding them to domain ontologies, and specifics about variable ranges, units, confidence scores, etc. Variable mentions identified in comments can be linked to mentions in the documents. Machine reading also extracts the context of equations, also linking and grounding mentions of variabels in equations. 
3. The *Equation Reading* pipeline extracts equations from PDFs, first identifying the latex source code that could produce the equation image, and then mapping the latex representation to a symbolic math representation. Equation Reading interacts with the Program Analysis pipeline by passing along the symbolic mathematical representation to perform the same analysis that extracts the source code Function Network and Lambdas, and interacts with the Machine Reading pipeline to ground equation variables to their context in the source text discourse.

The result of the coordinated Extraction and Grounding pipelines is a unified, programming language-agnostic intermediate representation that explicitly links the extracted information in the scientific discourse context and variables grounded in domain ontologies with the Function Network and Lambdas extracted in program analysis and equation extraction.  The *Grounded Function Network* (GrFN) intermediate representation captures all of this linked information in a form that permits further model analysis.



The following sections in the remainder of this report describe in detail the components of the architecture.  The numbers in the architecture summary figure correspond to the number of the section providing details about the component.
