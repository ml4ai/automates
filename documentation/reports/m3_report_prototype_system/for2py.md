### Open-ended Loop
`for2py` is able to read in Fortran open-ended loop code and translate it into fully working Python script.
The syntax of the open-ended loop in Fortran is `DO WHILE (condition)`. When the Open Fortran Parser (OFP)
reads in the Fortran script and generates the Abstract Syntax Tree (AST), it represents the DO WHILE loop
as an XML tag `<loop type="do-while">`. Then, `translate.py` processes and transforms this XML into IR
as a pickled Python object. Finally,`pyTranslate.py` translates the generated pickle file into Python script
that holds the open-ended loop syntax of `WHILE (condition):`.

### Array
The difference of array implementation, such as the starting index, explicit range assignment, and negative index,  
between Fortran and Python limits the direct translation of code. Therefore, the Python program needs to import
`for2py_arrays.py` class file and treat arrays as `Array` class objects that use `Array` class member functions (or methods)
to access the array values. In Fortran, arrays are declared as a dimension, for example, `REAL DIMENSION (10) :: X` 
is represented in Python as `X = Array([1, 10])`. Then, the Python program uses `set_(subs, val)` to set a value 
and `get_(subs)` to return the stored value.
Currently, `for2py` can handle both a single- and multidimensional arrays (e.g. `REAL DIMENSION (1:5, 1:10) :: Y`),
implicit and explicit range assignment, and negative index (e.g. `REAL DIMENSION (-10:10) :: Z`).
