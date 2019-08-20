## Program Analysis

### Constructs

The work on Program Analysis has focused on extending the set of Fortran language constructs that can be handled, focusing in particular on constructs that do not have straightforward analogues in our intermediate representation (IR) languages of Python and GrFN.  The following issues were a significant component of our efforts during this reporting period:

1. **GOTO statements.**  These are common in legacy Fortran code and occur in many places in the DSSAT code base.  Our approach to handling this construct is to eliminate GOTO statements by transforming the program's abstract syntax tree (AST) using techniques described in the paper "Taming Control Flow: A Structured Approach to Eliminating Goto Statements", by A. M. Erosa _et al._, Proceedings of 1994 IEEE International Conference on Computer Languages (ICCL'94), IEEE.

2. **Floating-point precision.** Fortran uses single-precision floating point values by default, while Python uses double-precision values.  While seemingly trivial, this difference can result in profound behavioral differences between a Fortran program and a naively-translated Python version of that code.  In order to preserve fidelity with the original models, we implemented a floating-point module in Python that faithfully models the behavior of Fortran floating-point computations and also explicitly represent associated precision within the GrFN representation.

3. **Lexical differences between Fortran dialects.** While expanding the set of source files handled, we encountered Fortran modules written in different dialects of Fortran, with different lexical rules (e.g., continuation lines are written differently in Fortran-90 than in Fortran-77).  These differences have to be handled individually, which can be time-consuming.  However, it gives us the ability to parse multiple dialects of the language and thereby broaden the programs we can handle.

In addition to these items, we also worked on handling a number of other language constructs in Fortran, including derived types and SAVE statements.

### DSSAT Code Coverage

The following is an estimate of the number of lines of code in the DSSAT code base that can be handled by the *parsing* components of Program Analysis. (Not all of this can yet be translated to GrFN.)  The DSSAT code base consists of the 162,290 lines of Fortran source code in 669 source files (not counting comments, which we handle separately). Program Analysis parsing can now cover 144,370 lines, which works out to a coverage of 89.0%.  An analysis of the constructs that are currently not handled shows two conclusions:

1. The number of remaining unhandled language constructs is not very large: 22 keywords.

2. A small number specific coding patterns, e.g., the mixing of single- and double-quotes in strings, together account for a large fraction of the remaining unhandled lines (i.e., other than the unhandled language constructs mentioned above).  The issues raised do not seem to be particularly difficult technically, and we expect to address them as we work down our prioritized list of goals.
