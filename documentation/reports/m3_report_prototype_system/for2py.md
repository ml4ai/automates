## FOR2PY

Our work in `for2py` has focused on extending the range of Fortran
language constructs handled.  We have implemented support for the
FORTRAN language constructs listed below.  In addition, we have mapped
out the translation of a number of additional FORTRAN language
constructs and are currently in the process of implementing their
translation.

**1. FORTRAN I/O**

FORTRAN's file-handling and formatted I/O handling mechanisms have been
implemented in the `for2py` IR. This gives us a way to validate the
front-end translation by comparing the observable behavior of the
generated Python code with that of the original Fortran code. In
particular, we have implemented the following:

1. _File Input_: Reading data in from a file. Analogous to Python's _read_line_.
2. _File Output_: Writing data onto a file in the disk. Analogous to Python's _write_.
3. _List-Directed Output_: Analogous to Python's _sys.stdout_. 

**2. Modules**

Modules provide a mechanism for programmers to organize their code,
control visibility of names, and allow code reuse; they are used
extensively in DSSAT as well as other scientific code bases.  We have
implemented the conversion of FORTRAN modules to the `for2py` IR, and
validated the translation by confirming that the resulting Python code
has the same behavior as the original FORTRAN code.

Our implementation translates each FORTRAN module into its own Python
file (named as _`m_<module_name>.py`_).  This has a number of
advantages, among them that it is easy to identify, isolate, and access
the Python code corresponding to each Fortran module, and also that the
Fortran module does not have to be analyzed and translated to Python
more than once.  Since Python does not have an explicit _`private`_
command to limit the visibility of names outside a given scope, we use
Python's name mangling to replicate the behavior of FORTRAN's `PRIVATE`
declarations.
    
We are currently working on implementing the translation of FORTRAN
modules from `for2py` IR into the GrFN specification language.


**3. Open-ended Loops**

`for2py` is able to translate Fortran `DO-WHILE` loops into an equivalent
Python IR.  We are currently working on implementing the translation of
such open-ended loops into the GrFN specification language.


**4. Arrays**

FORTRAN arrays differ from Python lists in a number of ways. By default,
FORTRAN arrays are 1-based, i.e., the first element is at index 1, while
Python lists are 0-based.  FORTRAN arrays can be declared to have lower
bounds different from the default value of 1; this is not true of Python
lists.  FORTRAN arrays can be multi-dimensional, while Python lists are
one-dimensional.  Finally, FORTRAN arrays support operations, such as
array constructors, various sub-array manipulations, array-to-array
assignments, etc., that do not have ready analogs in Python.  We have
implemented a library that implements Python objects that support
FORTRAN-like array operations.  Based on this library, we are currently
able to translate a wide range of FORTRAN array constructs into the
`for2py` IR.  In particular, we can handle the following FORTRAN array
features: single- and multidimensional arrays; implicit and explicit
array bounds; and read and write accesses to arrays.

We are currently working on implementing the translation of FORTRAN
arrays from `for2py` IR into the GrFN specification language.
