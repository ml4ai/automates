# Machine Reading

The purpose of this document is to describe the natural language processing (NLP) components
required for the automatic extraction of scientific information from academic papers,
including the description of equations and the variables that compose them,
along with the information required for the sensitivity analysis of the models of interest in this project.

## Automatic reading of scientific discourse expressed in natural language

This component is required for the identification of the regions of interest
in academic documents, as well as the extraction of entities and relations required for the 
grounding the models built by other components of our system.

This component is divided in two submodules: (A) in charge of the acquisition of information
such as ranges and units for variables, confidence scores such as p-values, and overall context
required for the automatic execution of our executable models. And (B), the identification of
sections of the document that describe equations and variables, as well as the extraction
of the relevant descriptions from those sections of text.

This includes the extraction of text from PDF files, optionally preserving the document
layout information. It also involves the development of grammars designed for the automatic
extraction of the information of interest. It is important for this component to comunicate
with other steps in the equation extraction pipeline for the acquisition of axis aligned bounding boxes (AABB)
that will be required for the identification of the relevant sections of text, as well as the equations
themselves and the variables that compose them.

## Grounding and linking

There are serveral aspects of grounding in this approach.  The first involves linking the variables
that are found in the source code with the corresponding comments, for example:
`TODO example from the fortran`

The second type of linking is similar, linking the variables and equations found in the scientific papers
with their descriptions.  For example, 
