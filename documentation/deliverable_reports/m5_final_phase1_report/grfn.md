## GrFN Specification

A Grounded Function Network (GrFN) serves as the central representation that integrates the extracted Function Network representation of source code (the result of Program Analysis) and associated extracted comments, links to natural language text (the result of Text Reading) and (soon) links to equations (the result of Equation Reading).

### Specification Links

The Month 5 Phase 1 release version of the GrFN Specification as of this report is linked here [GrFN Specification Version 0.1.m5](GrFN_specification_v0.1.m5). For the latest development version, see the [Delphi docs](https://ml4ai.github.io/delphi/grfn_spec.html).

### Updates

Since the [Month 3 Report on GrFN](https://ml4ai.github.io/automates/documentation/deliverable_reports/m3_report_prototype_system/#grfn-specification), we have made the following updates to the GrFN Specification:

- Added a "mutable" attribute to `<variable_spec>` to indicate whether a variable value can be changed (mutable) or is constant (immutable). While mutability is, strictly speaking, enforced implicitly by the wiring of functions to variables (as determined by Program Analysis), associating mutability with the variable is useful information to guide Sensitivity Analysis.
- Added a "variables" attribute to top-level `<grfn_spec>`, which contains the list of all `<variable_spec>`s. This change means that `<function_spec>`s no longer house `<variable_spec>`s, but instead just use `<variable_names>`s (which themselves are `<identifier_string>`s).
- Clarified the distinction between `<source_code_reference>`s (linking identifiers to where they are used in Program Analysis-generated lambdas file source code); previously these two concepts were ambiguous.
- Removed `<identifier_spec>` "aliases" attribute. This will be handled later as part of pointer/reference analysis.
- Did considerable rewriting of many parts of the specification to improve readability. Added links to help with topic navigation: now all `<...>` tags are linked to the sections in which they are defined (unless alread within that section).

