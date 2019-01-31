## FOR2PY

Support for the following FORTRAN language constructs have been added with progress being made on other constructs as well:
1. `FORTRAN I/O`
    FORTRAN's input/output handling mechanism has been successfully implemented into a Python intermeddiate such that the automatically generated Python file executes in a similar manner to the original FORRAN code. Aside from adding support to a vital language construct -- also an integral part of every scientific model codebase moving forward -- this support also allows for easy debugging and testing of the `for2py` module and it's functionality as a whole. Within I/O, the following features have full support implemented into Program Analysis:
    1. _`File Input`_: Reading data in from a file. Analogoues to Python's _read_line_.
    2. _`File Output`_: Writing data onto a file in the disk. Analogoues to Python's _write_.
    3. _`List-Directed Output`_: Writing to the console/terminal. This is useful for debugigng and testing of other FORTRAN module support. Analogous to Python's _sys.stdout_.

    `List-Directed Input` will be handled as a future work. With the handling of FORTRAN I/O, also comes the support for FORMAT statements which define the format in which data is to be read in or written out. An additional script `fortran_format.py` handdles parsing the FORMAT statemets into python ingestible data structures. 
    
2.  `Modules`
    Modules are another integral part of the FORTRAN lagnguage construct. FORTRAN modules provide a mechanism for programmers to organize their code, control visibility of names, and allow code reuse. Modules bring with itself the concept of `private variables`, `module functions` and `imports`. The current version of _`for2py`_ supports conversion of FORTRAN module statements in its respective representation in Python. Again, this Python intermeddiate script runs with the same behaviour as the original FORTRAN code.
    
    We assume that each FORTRAN module is translated into its own Python file (named as _`m_<module_name>.py`_).  This has a number of advantages, among them that it is easy to identify, isolate, and access the Python code corresponding to each Fortran module, and also that the Fortran module does not have to be analyzed and translated to Python more than once.
    
    FORTRAN's `USE` construct is now mapped into the `import` command in Python. FORTRAN supports universal as well as selective imports of variables, functions and subroutines. This is replicated in Python with the `from <module_name> import *` and `from <module_name> import <list of symbols>` commands.
    
    Python does not have an explicit _`private`_ command to keep variables and funtions as private but by using the name mangling mechanism, adding an underscore in front of variables/funtions ( _\_<variable_name>_ ) will limit their scope wihthin its function therefore effectively replicating the behaviour of FORTRAN's PRIVATE declarations.
    
    In addition to these, there are various corner cases in the implementation of Modules which will be handled moving forward.
