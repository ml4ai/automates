The function network described in the previous sections maps naturally
onto Delphi's representation of its internal model, i.e. a dynamic Bayes
network (DBN). [Delphi](https://github.com/ml4ai/delphi) was created as
part of DARPA's World Modelers program, to assemble quantitative,
probabilistic models from natural language.

Specifically, given causal relationships between entities extracted from
text, Delphi assembles a [linear dynamical system with a stochastic
transition
function](http://vision.cs.arizona.edu/adarsh/export/Arizona_Text_to_Model_Procedure.pdf)
that captures the uncertainty inherent in the usage of natural language
to describe complex phenomena.

More recently, Delphi's internal representation has been made more flexible to
accommodate the needs of the AutoMATES system, from updating the values of the
nodes via matrix multiplication to having individual update functions for each
node, that can be arbitrarily specified by domain experts - this enables us to
move beyond the linear paradigm. These individual update functions correspond to
the functions in the GrFN.

Note that while most scientific models of dynamical systems correspond to
*deterministic* systems of differential equations, lifting them into Delphi's
DBN representation allows us to treat the variables consistently as random
variables, associate probability distributions with their values, and conduct
sensitivity analysis.
