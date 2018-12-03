## 5. Model Analysis
Once we have lifted multiple scientific models from source code that compete with each other to represent the same phenomena we will enter the analysis phase. The two main goals of the analysis phase will be to compare model fitness and to augment existing models to create new models of the scientific phenomena under study that have improved upon existing models by one or more metrics. Some metrics we plan to consider are the amount of uncertainty in model output/predictions, the computational cost of the model, and the cost of data collection associated with the model.

### Function network structural comparison
The first step of comparative model analysis will be to compare the computational structure of the two competing models. All of our extracted models will be represented by factor networks. Below we describe the components of a factor network and then we discuss our plans to create an algorithm that can recursively compute the difference between two factor networks.

#### Factor graph description
A factor network consists of a set of variable nodes and factor nodes, similar to a factor graph. The additions that make this a network are that the edges in the graph are directed edges and a subset of the variable nodes are input nodes (meaning they have an in-degree of zero) and another subset of the variable nodes are output nodes (meaning they have an out-degree of zero). The variable nodes represent variables in the scientific model and the factor nodes represent the actual computations over the variables.

#### Recursive factor graph diff
As with any factor graph we can compare any two networks by doing a simple recursive network traversal. Since competing models of interest will likely have the same output node set, we plan to begin a recursive network traversal at the output nodes. By doing a network traversal we can trace the computation required by each model and see where the models perform the same computations and where they differ. Any difference in computation will be tracked as part of the model diff. The diff sections will be the subject of study for our sensitivity analysis measures.

There is a computability question that needs to be answered for performing a recursive network traversal. This amounts to performing a breadth-first search across the two models and thus the computational cost is considerable. To combat the concern of computational cost we are actively working on heuristics that can lower the cost associated with computing a network traversal for our particular purpose of model comparison.

### Input/output analysis
Once we have discovered where two competing models differ, we can begin to measure the different performance of the two models to determine comparative model fitness as well as sub-model fitness. Below we discuss two of the methods we plan on using to determine model fitness.  

#### Sensitivity analysis
The first method, sensitivity analysis, allows us to compare model output uncertainty as a function of the inputs. To perform sensitivity analysis we currently use the Python [SALib](https://salib.readthedocs.io/en/latest/index.html) package. Sensitivity analysis is conducted via the following steps:
1. Define domains for each of the model inputs
2. Compute `N` sets of samples over the input domains using [Saltelli's sampling method](https://www.sciencedirect.com/science/article/pii/S0010465509003087)
3. Evaluate the model for each of the `N` sets of samples
4. Compute the global sensitivity indices `Si` using [Sobol's method](https://www.sciencedirect.com/science/article/abs/pii/S0378475400002706)

The global sensitivity indices, `Si` can be split into three sub-components that each give us valuable information for assigning blame to input variables for uncertainty in the output. For each of the sets described below higher sensitivity index values correspond to having a greater affect on model output uncertainty.

- `S1` -- First-order index: measures amount of uncertainty in model output contributed by each variable individually. (Each member in the set represents a single input variable)
- `S2` -- Second-order index: measures amount of uncertainty in model output contributed by an interaction of two variables. (Each member in the set represents a unique pair of input variables)
- `St` -- Total-order index: measures amount of uncertainty in model output contributed by each variables first-order effects and **all** higher-order effects. (Each member in the set represents a single variable)

Using these sensitivity indices we can compare how similar inputs are used by competing models. This gives us an idea of comparative model fitness in terms of output uncertainty. We can also use this as a measure of sub-model fitness to determine which model makes the best use of certain inputs. This information can then be used during model augmentation to construct a new model that combines the most attractive parts of existing competing models to create a model that minimizes output uncertainty.

#### Value of information measures
The second method, value of information, allows us to quantify the value of input variables upon the output. This evaluation can be done in terms of the computational cost associated with a subset of inputs, or the cost associated with data collection (including the amount of data required) for a subset of inputs. In order to efficiently compute these measures we are investigating bayesian optimization frameworks that can be adapted to our specific use case (i.e. computed over a factor network).
