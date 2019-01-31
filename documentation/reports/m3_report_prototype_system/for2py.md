## FOR2PY

Support for the following FORTRAN language constructs have been added with progress being made on other constructs as well:
1. **FORTRAN I/O**
    
    FORTRAN's file-handling and formatted I/O handling mechanisms have been implemented in the `for2py` IR. This gives us a way to validate the front-end translation by comparing the observable behavior of the generated Python code with that of the original Fortran code. In particular, we have implemented the following:
    1. _`File Input`_: Reading data in from a file. Analogoues to Python's _read_line_.
    2. _`File Output`_: Writing data onto a file in the disk. Analogoues to Python's _write_.
    3. _`List-Directed Output`_: Analogous to Python's _sys.stdout_. 
    
2.  **Modules**
    
    Modules provide a mechanism for programmers to organize their code, control visibility of names, and allow code reuse; they are used extensively in DSSAT as well as other scientific code bases.  We have implemented the conversion of FORTRAN modules to the `for2py` IR. We have validate the translation by confirming that the resulting Python code has the same behavior as the original FORTRAN code.  
    
    Our implementation translates each FORTRAN module into its own Python file (named as _`m_<module_name>.py`_).  This has a number of advantages, among them that it is easy to identify, isolate, and access the Python code corresponding to each Fortran module, and also that the Fortran module does not have to be analyzed and translated to Python more than once.  FORTRAN's `USE` construct is mapped into the `import` command in Python. FORTRAN supports universal as well as selective imports of variables, functions and subroutines. This is replicated in Python with the `from <module_name> import *` and `from <module_name> import <list of symbols>` commands.  Since Python does not have an explicit _`private`_ command to limit the visibility of names outside a given scope, we use Python's name mangling to replicate the behavior of FORTRAN's PRIVATE declarations.


3.  **Open-ended Loops**

`for2py` is able to read in Fortran open-ended loops and translate them into equivalent Python IR.
The syntax of the open-ended loop in Fortran is `DO WHILE (condition)`. When the Open Fortran Parser (OFP)
reads in the Fortran script and generates the Abstract Syntax Tree (AST), it represents the DO WHILE loop
as an XML tag `<loop type="do-while">`. Then, `translate.py` processes and transforms this XML into IR
as a pickled Python object. Finally,`pyTranslate.py` translates the generated pickle file into Python script
that holds the open-ended loop syntax of `WHILE (condition):`.

4.  `Array`
The difference of array implementation, such as the starting index (1 in Fortran and 0 in Python), explicit range assignment, and negative index, between Fortran and Python limits the direct translation of code from Fortran-to-XML-to-Python script. Therefore, the Python program needs to import `for2py_arrays.py` class file and treat arrays as `Array` class objects that use `Array` class member functions (or methods) to access the array values. In Fortran, arrays are declared as a dimension, for example, `REAL DIMENSION (10) :: X` is represented in Python as `X = Array([1, 10])`. Then, the Python program uses `set_(subs, val)` to set a value of an array and `get_(subs)` to return the stored value.
Currently, `for2py` can handle a single-, multidimensional arrays, implicit and explicit range assignment, and negative index. For example, `REAL DIMENSION (2:5, -10:10) :: Y` in Fortran translates to `Y = Array([(2,5), (-10,10]))` in Python.
