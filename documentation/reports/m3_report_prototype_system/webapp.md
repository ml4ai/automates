## Demo Webapp

A demo of the current version of the prototype system is now live - you
can [try it out
here](http://ec2-13-57-207-3.us-west-1.compute.amazonaws.com)!

![Screenshot of AutoMATES demo webapp](figs/webapp_screenshot.png)

**Figure 1:** Screenshot of AutoMATES demo webapp

When Fortran source code is submitted to the demo, it is processed 
by the Program Analysis (`for2py`) pipeline, generating both (1) equivalent 
target executable Python internal representation and (2) matching GrFN 
specification representation. The GrFN specification is then rendered as a 
function network graph that you can interact with.

Currently, the demo has been only been tested with a limited number of
programs, so we encourage users as of now to experiment by modifying the
two suggested examples on the page, rather than trying to process
arbitrary Fortran programs. 

Clicking on the `__assign__` nodes in the rendered GrFN function network 
graph yields a LaTeX representation of the equation corresponding to the 
assign statement. This equation is constructed from the Python source 
represented using [`SymPy`](https://www.sympy.org), and will facilitate 
the linkage to equations extracted from papers using the equation parsing 
module.

For example, the screenshot above shows the analysis of the
Priestley-Taylor method of calculating potential evapotranspiration, as
implemented in DSSAT. Three of the `__assign__` functions have been
clicked, showing tooltips with black backgrounds containing some
of the equations involved in this calculation - these very equations can
be found on page 46 of the book [Understanding Options for Agricultural
Production](https://link-springer-com.ezproxy2.library.arizona.edu/book/10.1007%2F978-94-017-3624-4)
(reproduced below - the equations matching the ones in the screenshot of
the webapp are highlighted with maroon borders).

---

![Page 46 of the book Understanding Options for Agricultural
Production](figs/petpt_equations_example.png)


**Figure 2:** Page 46 of the book _Understanding Options for Agricultural Production_, describing the Priestley-Taylor method of calculating potential evapotranspiration.
