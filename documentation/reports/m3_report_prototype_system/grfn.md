## Updates to GrFN representation

During this phase, significant extensions were made to the GrFN specification that serves as the central representation between program analysis (which extracts variables and the network of functions among them) and model analysis (where the variables and their functional relationships are treated generally as a probabilistic dynamic systems model). The extensions include the following:

- The introduction of `Identifiers`. Prior to this update, a variety of naming conventions were used to represent source code identifiers (names for program entities such as variables, constants, functions, etc.), and the disambiguating context in which they are defined. Identifiers now systematically represent *namespaces* and program *scope* as part of definition of an identifier, along with its *base name*. The representation of identifiers includes the following additions and advantages:

	- `<identifier_spec>` declarations in GrFN associate identifier usage, such as the location within source code of where the identifier was declared, as well as \"aliases\" (other names used to refer to the same program elements). The location of identifier use will be used to connect identifiers with source code comments and documentation strings. Also, the base names themselves, and their namespace names, will be used as evidence for *grounding* variables to domain concepts.
	
	- Inclusion of namespace and scope context in identifier definitions make it possible for program analysis to capture the naming context of Fortran program Modules, and also provide a consistent method extending source code representation beyond single files.
	
	- An `<identifier string>` provides a single human-readable instance of an identifier. These will be used to denote instances of identifiers use in generated GrFN JSON (outside of the identifier declaration specs). For example, \"CROP\_YIELD::UPDATE\_EST::YIELD\_EST\" is an identifier for a variable name originally given as \"YIELD\_EST\" in source code, but defined in the \"CROP\_YIELD\" namespace, and within the \"UPDATE\_EST\" function scope.
	
	- Since identifiers are themselves now a function of structured information (namespace, scope, and base name), identifier `<gensym>`s have been introduced to used as standins for identifiers in generated intermediate target Python code.

- The new systematic representation of namespace and scope rules for identifiers allows for cleanup of the previous ad-hoc approach to naming variables and functions. New naming conventions have been introduced.

- The approach to representing conditions was also updated. When program analysis analyzes a conditional in source code, a \"condition\" assignment function is introduced that sets the state of a variable representation the condition, and then one or more \"decision\" assignment functions are introduce that represent updates to other variables depending on the outcome of the variable.

- Finally, there was a significant rewrite of the specification introduction as well as updates throughout the specification to improve readability and ensure consistency. 

The release version of the GrFN specification, as of this report (Version 0.1.m3), is linked [here](GrFN_specification_v0.1.m3). (For the latest development version, see the [delphi read the docs page](https://delphi.readthedocs.io/en/master/grfn_spec.html).)

