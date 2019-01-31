## FOR2PY

Support for the following FORTRAN language constructs have been added with progress being made on other constructs as well:
1. `FORTRAN I/O`
    FORTRAN's file-handling and formatted I/O handling mechanisms have been implemented in the for2py IR. This gives us a way to validate the front-end translation by comparing the observable behavior of the generated Python code with that of the original Fortran code. In particular, we have implemented the following:
    1. _`File Input`_: Reading data in from a file. Analogoues to Python's _read_line_.
    2. _`File Output`_: Writing data onto a file in the disk. Analogoues to Python's _write_.
    3. _`List-Directed Output`_: Analogous to Python's _sys.stdout_.

    `List-Directed Input` will be handled as a future work. With the handling of FORTRAN I/O, also comes the support for FORMAT statements which define the format in which data is to be read in or written out. An additional script `fortran_format.py` handdles parsing the FORMAT statemets into python ingestible data structures. 
    
2.  `Modules`
    Modules are another integral part of the FORTRAN lagnguage construct. FORTRAN modules provide a mechanism for programmers to organize their code, control visibility of names, and allow code reuse. Modules bring with itself the concept of `private variables`, `module functions` and `imports`. The current version of _`for2py`_ supports conversion of FORTRAN module statements in its respective representation in Python. Again, this Python intermediate script runs with the same behaviour as the original FORTRAN code.
    
    We assume that each FORTRAN module is translated into its own Python file (named as _`m_<module_name>.py`_).  This has a number of advantages, among them that it is easy to identify, isolate, and access the Python code corresponding to each Fortran module, and also that the Fortran module does not have to be analyzed and translated to Python more than once.
    
    FORTRAN's `USE` construct is now mapped into the `import` command in Python. FORTRAN supports universal as well as selective imports of variables, functions and subroutines. This is replicated in Python with the `from <module_name> import *` and `from <module_name> import <list of symbols>` commands.
    
    Python does not have an explicit _`private`_ command to keep variables and funtions as private but by using the name mangling mechanism, adding an underscore in front of variables/funtions ( _\_<variable_name>_ ) will limit their scope wihthin its function therefore effectively replicating the behaviour of FORTRAN's PRIVATE declarations.
    
    In addition to these, there are various corner cases in the implementation of Modules which will be handled moving forward.

3.  `Open-ended Loop`
`for2py` is able to read in Fortran open-ended loop code and translate it into fully working Python script.
The syntax of the open-ended loop in Fortran is `DO WHILE (condition)`. When the Open Fortran Parser (OFP)
reads in the Fortran script and generates the Abstract Syntax Tree (AST), it represents the DO WHILE loop
as an XML tag `<loop type="do-while">`. Then, `translate.py` processes and transforms this XML into IR
as a pickled Python object. Finally,`pyTranslate.py` translates the generated pickle file into Python script
that holds the open-ended loop syntax of `WHILE (condition):`.

4.  `Array`
The difference of array implementation, such as the starting index (1 in Fortran and 0 in Python), explicit range assignment, and negative index, between Fortran and Python limits the direct translation of code from Fortran-to-XML-to-Python script. Therefore, the Python program needs to import `for2py_arrays.py` class file and treat arrays as `Array` class objects that use `Array` class member functions (or methods) to access the array values. In Fortran, arrays are declared as a dimension, for example, `REAL DIMENSION (10) :: X` is represented in Python as `X = Array([1, 10])`. Then, the Python program uses `set_(subs, val)` to set a value of an array and `get_(subs)` to return the stored value.
Currently, `for2py` can handle a single-, multidimensional arrays, implicit and explicit range assignment, and negative index. For example, `REAL DIMENSION (2:5, -10:10) :: Y` in Fortran translates to `Y = Array([(2,5), (-10,10]))` in Python.
