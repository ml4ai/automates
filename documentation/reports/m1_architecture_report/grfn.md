The Intermediate Representation is the focal point of the AutoMATES
representation: it is the programming language-agnostic target of Extraction and
Grounding processes, capturing the model context by linking all of the
information extracted from the input information sources, and serves as the
basis for contextualized model analysis and Augmentation.  This information is
combined in the unified The *Grounded Function Network* (GrFN) representation.
The modular representation of variable-setting functions in the *Lambdas*
representation is described in the next section on Program Analysis; Lambda
function modules are referred to in the GrFN specification of a model.

We use a JSON format for the GrFN specification for simple serialization,
deserialization, and compatibility with web APIs.  The current state of the GrFN
specification is described here: [GrFN specification](GrFN_specification_v0.1)
