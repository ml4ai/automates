A demo of the current version of the prototype system is now live - you
can [try it out
here](http://ec2-13-57-207-3.us-west-1.compute.amazonaws.com)!

![Screenshot of AutoMATES demo webapp](figs/webapp_screenshot.png)

Currently the demo has been tested with a limited number of programs, so
we encourage users as of now to experiment by modifying the two
suggested examples on the page, rather than trying to process arbitrary
Fortran programs. 

Clicking on the assign nodes yields a LaTeX representation of the
equation corresponding to the assign statement. This equation is
constructed using `SymPy`, and will facilitate the linkage to equations
extracted from papers using the equation parsing module.
