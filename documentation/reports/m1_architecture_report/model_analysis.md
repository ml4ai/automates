The GrFN and Lambdas Intermediate Representation grounds computational
scientiic models in context of their descriptions and connections to
domain ontologies.  At this point, we can perform Model Analysis in a
unified framework, with on individiaul models, or more importantly in
the service of comparing and contrasting two or more models.  The two
main goals of this phase are to compare model fitness to a task and to
Augment existing models to improve them in a task context according to
one or more metrics, such as the amount of uncertainty in model
output/predictions, the computational cost of the model, and the
availability (or cost) of data in order to callibrate and use a model.

### Function network structural comparison 

The first step of comparative model analysis will be to compare the
computational structure of the two competing models. All of our
extracted models will be represented by *Factor Networks*. Below we
describe the components of a factor network and then discuss plans to
develop an algorithm that can recursively compute the similarity and
difference between two factor networks.

#### Factor graph description 

A factor network consists of a set of variable nodes and factor nodes,
similar to a [factor
graph](https://en.wikipedia.org/wiki/Factor_graph). The additions that
makes this a *network* are that the edges in the graph are directed
edges and a subset of the variable nodes are input nodes (meaning they
have an in-degree of zero) and another subset of the variable nodes
are output nodes (meaning they have an out-degree of zero). The
variable nodes represent (grounded) variables in the scientific model
and the factor nodes represent the functions that determine the state
of the output variable as a function of zero or more input variables.

#### Recursive factor graph diff

As with any factor graph we can compare any two networks by doing a
simple recursive network traversal. When competing models of interest
share (subset of) the same output node set, we begin a recursive
network traversal from the output nodes that traces the computation
required by each model and identifies where the models perform the
same computations and where they differ. Any difference in computation
will be tracked as part of the model diff. The result is a partition
into function network modules that are either found to be similar, or
constitute different (no-overlapping) components.  These modules are
then the subject of study for our sensitivity analysis measures.

There is a computability question that needs to be answered for
performing a recursive network traversal.  The network comparsion
computation is expected to be potentially complex as this amounts to
performing a breadth-first search across the two models.  We are
working on heuristics that can lower the cost associated with
computing a network traversal for our particular purpose of model
comparison.

### Input/output analysis

Once we have identified the similar (overlapping) and different
components of the models, we can estimate the sensitivity of module
output variables to input variable values by estimating how relative
changes in module input impact the functional output of variables.
When comparing two overlapping modules, we can identify differences in
model sensitivity.

We will take two approaches to analyzing 

#### Sensitivity analysis

Sensitivity analysis allows us to compare model output uncertainty as
a function of the inputs. To perform sensitivity analysis we will
start by using the open source Python
[SALib](https://salib.readthedocs.io/en/latest/index.html)
package. Sensitivity analysis is conducted via the following steps:

1. Define domains for each of the model inputs (to the extend
possible, this information will be automatically associated with GrFN
model representation as a result of Extraction and Grounding).

2. Compute `N` sets ofsamples over the input domains using [Saltelli's
sampling
method](https://www.sciencedirect.com/science/article/pii/S0010465509003087).

3. Evaluate the model for each of the `N` sets of samples 4. Compute
the global sensitivity indices `Si` using [Sobol's
method](https://www.sciencedirect.com/science/article/abs/pii/S0378475400002706)

The global sensitivity indices, `Si`, are split into three
sub-components that each give us valuable information for assigning
"blame" to input variables for uncertainty in the output. For each of
the sets described below, higher sensitivity index values correspond to
having a greater affect on model output uncertainty.

- `S1` -- First-order index: measures amount of uncertainty in model
  output contributed by each variable individually. (Each member in
  the set represents a single input variable)

- `S2` -- Second-order index: measures amount of uncertainty in model
  output contributed by an interaction of two variables. (Each member
  in the set represents a unique pair of input variables)

- `St` -- Total-order index: measures amount of uncertainty in model
  output contributed by each variables first-order effects and **all**
  higher-order effects. (Each member in the set represents a single
  variable)

Using these sensitivity indices we can compare how similar inputs are
used by competing models. This gives us an idea of comparative model
fitness in terms of output uncertainty. We can also use this as a
measure of sub-model fitness to determine which model makes the best
use of certain inputs. This information can then be used during model
augmentation to construct a new model that combines the most
attractive parts of existing competing models to create a model that
minimizes output uncertainty.

#### Efficient Sensitivity Analysis

Estimating sensitivity functional relationships through sampling can
be expensive if performed naively.  In particular, it requires
repeated evaluation of the code module, choosing different variable
values to assess the impact on other variables. In order to enable
scaling of sensitivty analysis to larger Factor Networks, we will
explore the following three additions to the AutoMATES Model Analysis
architecture.

1. The building-block of sensitivity analysis is estimation of partial
derivatives of output variables as a function of their input variabls.
We will explore using automatic source code differentiation methods,
starting with the Python [Tangent](https://github.com/google/tangent)
package to derive differentiated forms of Lambdas for direct
derivative function sampling.

2. We will adapt methods from Bayesian optimization, in particular the
computation of the Bayesian optimal value of infomration of selecting
a particular input combination for reducing undertainty in the
estimation of the sensitivity function.

3. Finally, in conjunction with the two techniques above, we will
explore using compiler optimization methods to compile differentiated
lambda functions into efficiently executable code.

