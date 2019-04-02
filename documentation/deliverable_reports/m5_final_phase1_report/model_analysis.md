## Model Analysis

Inputs to the Model Analysis pipeline come from the Program Analysis, Text Reading, and Equation Reading pipeline outputs. The Program Analysis module provides a wiring specification and a set of associated lambda functions for the GrFN computation graph. Together these fully describe the structure of a scientific model found in source code. The output from Text Reading and Equation Reading are combined in the GrFN specification in order to ground the variables used in computation. This information is critical for the model comparison phase of Model Analysis. The Model Analysis module utilizes all of these inputs, as well as similar sets of inputs for other scientific models, to generate a model report, the output result of the Model Analysis pipeline. The eventual goal of the model report is to contains all information recovered and inferred during Model Analysis about the sensitivity of the model to various inputs over various ranges and, if requested, information about comparative model fitness to other models of the same output. As of this Phase 1 release of the AutoMATES Prototype, individual components of a model report are generated during Model Analysis, but the integration and format of the final report under development. In the following we describe the current state of the Model Analysis components.

### Architecture

The architecture for the Model Analysis module is shown in Figure 18. The overall structure of the module is a pipeline that transforms extracted information from text, equations, and software into a report about a scientific model. However, this pipeline has optional additional components (represented by dashed input arrows) that can be included in the final model report based upon the amount of information requested by the user. In this section we will describe the intermediate objects created during model analysis as well as the algorithms used during their generation.

![Model Analysis architecture](figs/model_analysis/model-analysis.png)

**Figure 18:** Model Analysis architecture

#### Computation graph generation
Generating an actual computation graph from a GrFN spec and lambdas requires two phases, a wiring phase and a planning phase. The output from these two phases will be an executable computation graph.

- **Wiring phase**: This phase utilizes the GrFN specification of how variables are associated with function inputs and outputs in order to "wire together" the computation graph. 

- **Planning phase**: In this phase, a partial order is imposed over the lambda functions in the call graph of the GrFN, to determine an efficient order of computation and discover sets functions that can potentially be executed in parallel. The ordering is recovered using `HeapSort` on the function nodes in the computation graph, where the heap invariant is the distance from the function node to an output node. The output of this algorithm is a call stack that can be used to execute the `GrFN` computation graph. After this phase is completed the computation graph can be executed as many times as needed without requiring a graph traversal per computation, allowing for more efficient sampling and sensitivity analysis.

An example of the `GrFN` computation graph for `PETASCE` (the ASCE Evapotranspiration model) is shown in Figure 19.

![PETASCE GrFN computation graph.](figs/model_analysis/petasce_grfn.png)

**Figure 19:**: PETASCE GrFN computation graph.

In the figure, variable are represented by ovals and functions by boxes. The function nodes are labeled by a single-letter code denoting the type of function computed - these correspond to the same labels in the [CodeExplorer Function Network description](#function-network).

#### Model comparison

Computation graphs can be used as the basis to compare models. First we identify what variables are shared by the two models. We can then explore how the models are make similar (or different) assertions about the functional relationships between the variables. 

Of course the functions between the variables may be different, and other variables that are not shared might directly affect the functional relationships between the shared variables. The goal of 

Given the computation graphs for two models, we first identify the overlap in their variable nodes. In the examples we consider here, this is done using variable base-name string matching, since we are comparing two models from DSSAT, and the variables have standardized names in the code; more generally, we will rely on variable linking using information recovered from Text and Equation Reading. Once we have a set of shared variables, we then identify the subgraphs of each model that contain all directed paths from input shared variables to output shared variables. As part of this, we also identify any other variables in the model that serve as direct inputs to the functions along the paths between input and output shared varaibles. These additional, direct input variables that are not shared are referred to as the _cover set_ of the subgraph. These are variables whose state will affect the how the shared variables relate.

As a final step, we look to see if any variables in the cover set are assigned values by a literal function node. We remove these variable nodes from the cover set, and add them and their literal assignment function node directly to the subgraph. The combination of shared variable input nodes, cover set variable nodes, and additional wiring forms a `Forward Influence Blanket` or `FIB` for short. An example of the `FIB` for the `PETASCE` model is shown in Figure 20. Here we can see the shared input variables colored in blue, while the _cover set_ variables are colored green.

![PETASCE GrFN Forward Influence Blanket.](figs/model_analysis/petasce_fib.png)

**Figure 20:** PETASCE GrFN Forward Influence Blanket.

The identified `FIB` of each model then forms the basis for directly comparing the components shared between the models. An open challenge is to automate identification of _cover set_ variables value ranges that make the functional relations between shared variables achieve the same input-to-output functional relationships between the two models (or as close the same as possible). As of this report, we assume these value ranges are identified. Given these value ranges, we can then contrast the two model `FIB`s by performing sensitivity analysis over the shared variables.

#### Sensitivity analysis and model reporting

[Sensitivity analysis](https://en.wikipedia.org/wiki/Sensitivity_analysis) identifies the relative contribution of uncertainty in input variables (or variable pairs, in second order analysis) to uncertainty in model output. 
In the current AutoMATES Prototype, we use use the [SALib](https://github.com/SALib/SALib) python package for performing several types of sensitivity analsyis. The package provides functionality to sample from our input variable space(s) and estimate output sensitivity over an input space.
We have created a simple API that takes a `GrFN` computation graph along with a set of search bounds for all model inputs and computes the sensitivity indices associated with each input or pairs of inputs.

The sensitivity indices that are returned from a call to the sensitivity analysis API can be used to determine what information about a model is worth including in the model report.
For a report about a single model we will likely be interested in which variables or which pairs of variables contribute the most to output uncertainty.
Once we have recovered the indices we can plot the response of a target output variable as a function of the input (or pair of inputs) that contributes the most to the uncertainty in the output variable.

### Instructions for running components

The model analysis pipeline has been integrated into the [CodeExplorer](#codeexplorer) web application. Users can visualize the outputs from model analysis by loading one of the provided Fortran programs and inspecting the GrFN Computation Graph along with its associated Function Call Graph and Causal Analysis Graph. In addition, for the `PETPT` (Priestley-Taylor) model, users can visualize the sensitivity surface generated by the `S2` index of highest degree: the effects of changes in `srad` and `t-max` on the output variable `eo`; this is plotted in the sensitivity surface tab.

This functionality can also be programmatically accessed using the [S2_surface](https://ml4ai.github.io/delphi/delphi.GrFN.html#delphi.GrFN.networks.GroundedFunctionNetwork.S2_surface) method of the [GroundedFunctionNetwork](https://ml4ai.github.io/delphi/delphi.GrFN.html#delphi.GrFN.networks.GroundedFunctionNetwork) class.

### Current caveats

Currently we are using the `PETPT` and `PETASCE` modules for the evaluation of our model analysis module. This comes with certain advantages as well as challenges.

One advantage of these modules is that variables that represent the same real-world object have the exact same names. This enables us to easily conduct model comparison experiments on these models without relying on potentially noisy variable linking from the Text Reading module. In future iterations our model comparison component will rely on variable link hypotheses from Text Reading.

One obstacle we needed to overcome in order create an executable computation graph for the `PETASCE` model was the identification of the range of possible values variables may take on. The `PETASCE` model includes calls to several functions that have restricted value domains, such as `log` and `acos`. The `PETASCE` model itself contains no explicit guards against inputs values that are "out-of-domain" (mathematically undefined) for these functions, thus domains for each input variable must be discovered via analysis. We are currently developing a component of the Model Analysis module that will infer input variable domain value constraints. Currently, the `GrFN` computation graph catches value exceptions to gracefully alert the sampling component of failure to execute, but in the near future we hope to infer bound information directly.

### Updates

- **End-to-end generation**: Our previous results from Model Analysis were based on running analysis methods over translated Python programs from original Fortran source code or hand-constructed `CAG`s for model comparison. We are now able to conduct all the steps of Model Analysis directly on the GrFN representation generated by the Program Analysis team.

- **Vectorized model evaluation**: We have begun experimenting with vectorizing the execution of the computation graph using the [PyTorch](https://pytorch.org/) tensor computation framework, which provides a useful general interface to GPU resources. This provides speed up for sampling.
Evaluation using PyTorch required a few changes to the GrFN specification and generated lambda functions. Preliminary experiments suggest that vectorization using PyTorch increases sampling on a CPU speed by a factor of $$\sim 10^3$$, and this increases to $$\sim 10^6$$ when using GPU resources. This evaluation is ongoing.

- **Additional SA methods**: Due to the computational cost of `Sobol` sensitivity analysis, we have explored two new methods of sensitivity analysis - the [Fourier Amplitude Sensitiity Testing (FAST)](https://en.wikipedia.org/wiki/Fourier_amplitude_sensitivity_testing) and the variant `RBD-FAST` sensitivity analysis methods - to our suite of analysis tools. While these methods can only be used for computing first-order sensitivity indices, their compute time scales constantly with number of samples (for comparison, Sobol analysis scales linearly). Figure 21 demonstrates these runtime differences; these results were generated by running all of our sensitivity methods on the `PETPT` model.

![Sensitivity analysis compute times.](figs/model_analysis/SA_compute_time.png)

**Figure 21**: Sensitivity analysis compute times.
