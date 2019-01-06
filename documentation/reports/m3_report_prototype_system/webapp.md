A [demo of the current version of the prototype
system](http://ec2-13-57-207-3.us-west-1.compute.amazonaws.com) has been set up
on AWS. It has has currently been tested with the toy fortran program below
(you can copy and paste the code into the editor in the demo webapp):

```fortran
{% include_relative crop_yield.f %}
```

Clicking on the assign nodes yields a $$\LaTeX$$ representation of the equation
corresponding to the assign statement. This equation is constructed using `SymPy`,
and will facilitate the linkage to equations extracted from papers using the
equation parsing module.

{:comment}
TODO : Insert screenshot of webapp here.
{:/comment}
