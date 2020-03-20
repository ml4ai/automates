## Program Analysis: for2py

Our work in `for2py` has focused on extending the range of Fortran
language constructs handled.  We have implemented support for the
Fortran language constructs listed below.  In addition, we have mapped
out the translation of a number of additional Fortran language
constructs and are currently in the process of implementing their
translation.

### Fortran I/O

Fortran's file and formatted I/O handling mechanisms have been implemented in `for2py` so that the pipeline now generates functionally equivalent Python intermediate representation. This gives us a way to validate the front-end translation by comparing the observable behavior of the generated Python code with that of the original Fortran code. In particular, we have implemented the following:

1. _File Input_: Reading data in from a file. Analogous to Python's _read_line_.
2. _File Output_: Writing data to a file in the disk. Analogous to Python's _write_.
3. _List-Directed Output_: Analogous to Python's _sys.stdout_. 

### Fortran Modules

Fortran Modules provide a mechanism for programmers to organize their code,
control visibility of names, and allow code reuse; they are used
extensively in DSSAT as well as other scientific code bases.  We have
implemented the conversion of Fortran modules to the `for2py` intermediate representation, and validated the translation by confirming that the resulting Python code
has the same behavior as the original Fortran code.

Our implementation translates each Fortran module into its own Python
file (named as _`m_<module_name>.py`_).  This has a number of
advantages, among them that it is easy to identify, isolate, and access
the Python code corresponding to each Fortran module, and also that the
Fortran module does not have to be analyzed and translated to Python
more than once.  Since Python does not have an explicit _`private`_
command to limit the visibility of names outside a given scope, we use
Python's [name mangling](https://docs.python.org/2/tutorial/classes.html#private-variables-and-class-local-references) to replicate the behavior of Fortran's `PRIVATE`
declarations.
    
We are currently working on implementing the translation of Fortran modules from `for2py` intermediate representation into the GrFN specification language, where we will make use of the new `identifier` and naming conventions.


### Open-ended Loops

`for2py` is able to translate Fortran `DO-WHILE` loops into an equivalent Python intermediate represetnation.  We are currently working on implementing the translation of such open-ended loops into the GrFN specification language.


### Arrays

Fortran arrays differ from Python lists in a number of ways. By default, Fortran arrays are 1-based, i.e., the first element is at index 1, while Python lists are 0-based.  Fortran arrays can be declared to have lower bounds different from the default value of 1; this is not true of Python lists, which always start with index 0.  Fortran arrays can be multi-dimensional, while Python lists themselves are one-dimensional.  Finally, Fortran arrays support operations, such as array constructors, various sub-array manipulations, array-to-array assignments, etc., that do not have ready analogs in Python.  We have implemented a library that implements Python objects that support Fortran-like array operations.  Based on this library, we are currently able to translate a wide range of Fortran array constructs into the `for2py` intermediate representation.  In particular, we can handle the following Fortran array features: single- and multidimensional arrays; implicit and explicit array bounds; and read and write accesses to arrays.

We are currently working on implementing the translation of Fortran arrays from `for2py` intermediate representation into the GrFN specification language.
