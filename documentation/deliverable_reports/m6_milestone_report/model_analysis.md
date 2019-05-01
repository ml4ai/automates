## Model Analysis

#### Model Constraint Propagation
During phase 1 the model analysis team identified instances of input sets to the PETASCE Evapo-transpiration model that caused bound errors during evaluation. This is due to the bound constraints of certain mathematical functions used in PETASCE, such as `arccos` and `log`. These constraints can be buried deep within the model architecture and commonly place shared constraints on more than one variable value. Some examples of constraints found in the PETASCE model are shared below.

```Fortran
RHMIN = MAX(20.0, MIN(80.0, EA/EMAX*100.0))   ! EMAX must not be 0
RNL = 4.901E-9*FCD*(0.34-0.14*SQRT(EA))*TK4   ! EA must be non-negative

! The inner expression is bounded by [-1, 1] and this bound propagates to
! expression of three variables.
WS = ACOS(-1.0*TAN(XLAT*PIE/180.0)*TAN(LDELTA))
```

Automating the process of sensitivity analysis for any input set will require static analysis to determine the set of domain constraints that can be used to validate an input. Then when running a model the first step will be to validate the input set to ensure that the inputs fit within the domains. For sensitivity analysis that includes a sampling step over a set of bounds this will require validation of the runtime bounds and possibly amending the sampling process for different sensitivity methods to ensure that samples are not taken from areas out of the constrained domain. Currently the MA team is working on a method to determine the bounds for a model by doing a forward/backward pass of bounds over the model, starting with calculating the range of variables in a forward pass and then using this information to calculate the domains of variables during the backward pass.

#### Representing Collections in GrFN
We wish to represent our GrFN models as dynamic Bayes nets. Therefore all variables included in the Bayes net must have a single state that can be represented in the graphical model. This posses a representation problem for collection objects found in source code. The most common collection object found in source code is an array. We plan on handling array objects by treating each variable contained within the array as a variable in the GrFN computation graph. These variables can be accessed from the array via a getter function and values can be set to specific variables in the array using a getter function. This functionality mirrors the functionality of getters/setters for members of a collection that are common in many source code languages and allows for uses and assignments to members of an array collection to be visibly specified as part of the GrFN computation graph. Moreover the introduction of specific getter/setter functions to gain access to variables contained in a collection is generalizable to collections other than arrays. Indeed this formulation is generic enough to allow for any collection or container type to be well-represented in a GrFN computation graph by explicitly showing any actions that involve its member variables.
