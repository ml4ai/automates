## Model Analysis

#### Domain Constraint Propagation
###### Task Overview
The overall goal of the domain constraint propagation task is to find the minimum functional bounds on each of the inputs for a GrFN such that no set of input values will fail to evaluate due to a mathematical error.
Concretely, minimal functional bounds are bounds that arise upon the inputs to a given computation because of the functions computed in the course of that computation.
An example of this would be the `arcsine` function, whose domain is `[-1, 1]`.
If the following function were present in source code, `y = arcsine(x)` then a constraint would be placed on the domain of `x` such that it would be `[-1, 1]` at most.
In general, programs extracted from the Program Analysis team are likely to have complex interactions between variables and mathematical operations that lead to domain constraints.
This means that the domain constraints of a single variable are likely going to be in terms of the other variables.
This means that solutions to our domain constraint propagation problem will likely be in the form of a constraint satisfaction problem (CSP) with variables that have infinite domains.
Normally time complexity is a concern for CSP problems even upon finite domains; however, those time constraints are associated with determining if the set of constraints has a solution.
Our intended use case for this is as a recognizer for whether a set of input values will cause a mathematical error in calculation, so we need not worry about the widely studied time complexity concerns associated with CSPs.

The following are all true about domain constraints derived from the computations found in source code:
1. Some mathematical functions _set_ domain constraints upon the variables in their child structures.
2. Some mathematical functions _translate_ domain constraints upon the variables in their child structures.
3. Some mathematical functions create complex multi-interval domain constraints.
4. Conditional evaluations introduce multiple possible domain constraints over for a variable

From fact `1` items we see that the domain constraint for a particular variable will be set by mathematical functions that impose constraints on their inputs, such as arccosine and the logarithm function.
These constraints will be in the form of mathematical domain intervals.
Other operators will shift or scale the domain constraints intervals upon a variable, such as the addition, multiplication, and exponentiation operators.
Fact `3` shows us that a particular variables domain could be a series of intervals.
This can occur due to functions that impose domains with holes, such as the division operation.
Now a domain constraint upon a variable can be described as a list of domain intervals for an input variable over which the output can be computed.
But, as mentioned by fact `4`, the presence of conditionals adds complications to the domain constraints for a variable.
Now the domain constraint must be based on the conditional evaluation in cases where two separate mathematical functions make use of a variable in a constrained manner as governed by a conditional.
Since our plan is to use the domain constraints discovered during the propagation process to validate input sets, we will use the most restrictive case for conditionals which will be to require any variable domains found under conditionals to fulfill the constraints of all branches of the conditional.

###### Algorithmic Solver Approach
Our approach to solving the domain constraint propagation problem will be to create an algorithmic solver that uses the structure of the source code that we extract our models from in order to create a graph of the constraints upon the domains of different variables.
The algorithmic solver will perform a line-by-line walk through the code, and will perform a tree-walk at each line of the code, generating and updating variable constraints upon visiting operators on each line.
To visualized the tree-walk that will occur for each line of code, consider the example complex mathematical equation shown below.
```python
a = arccosine(logarithm((x*y)/5)) * square_root(z)
```
This can be rewritten in the following form with only one mathematical operation per-line to show how a tree-walk will occur:
```python
(1) n0 = x * y
(2) n1 = n0 / 5
(3) n2 = logarithm(n1)
(4) n3 = arccosine(n2)
(5) n4 = square_root(z)
(6) a = n3 * n4
```
If we evaluate, in a similar manner as the tree-walk will occur, from line 6 backwards to line 1 we can see how the domain constraints will propagate to the input variables, such as how the domain constraint introduced by `arccosine` is propagated from `n2 --> n1 --> n0 --> x & y`.
Just as this process has been carried out for a single line mathematical function, the same tree-walk can be done across lines to propagate variable constraints backwards to all the input variables of a scientific model.
Using this method works very well for straight-line code; however there are atleast two questions that still need to be answered:
1. How will this method work for function calls?
2. How does this method handle loops?

For problem `1`, if we can observe the code for a function call then we can treat the function exactly the same as we would straight-line code.
If we cannot observe the code for a function call, but we do know it's domain/range then we can treat this function just like any other mathematical operator upon its inputs and outputs.
However, if we cannot observe the functions code and we do not have any information of its inputs or outputs then we will be unable to determine the validity of solutions to the domain constraint problem.
For problem `2`, if we know the number of times we are expected to loop then we can guarantee whether input sets satisfy the domain constraints; otherwise, we can perform this analysis on the loop as though it is straight-line code with a conditional.

#### Model Output Space Analysis
###### Task Overview

###### Ibex and dReal Satisfiability Tools

###### Current Status
