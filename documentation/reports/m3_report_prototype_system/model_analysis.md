## Model Analysis

A key goal of model analysis is to enable comparison of models that describe the underlying target domain. When the models overlap, they share some variables, but likely not others. The first task in comparing GrFN function networks is to identify where the models overlap. We first review the team's work on automating function network comparison, and then present some initial results investigating the complexity of running sensitivity analysis, which in turn is informing our next approaches to scaling sensitivity analysis.

### Automated function network comparison

During this phase, the team developed an algorithm to identify the shared portion of
two function networks. As a working example, we show what the algorithm identifies as the overlapping subnetworks of two evapotranspiration models in the DSSAT system: ASCE and Priestley-Taylor.
The following two figures show a graphical representation of the shared portions of these two models, which are identified by a network property that we refer to as a _Forward Influence Blanket_ (FIB). In the following section we will formally define the structure of a FIB and its role in model analysis.

---

![Representation of the subnetwork within the Priestley-Taylor model identified by the Forward Influence Blanket that intersects with the ASCE model](figs/full-pt-cmb.png)

**Figure 4:** Representation of the subnetwork (blue and black nodes) within the Priestley-Taylor model identified by the Forward Influence Blanket that intersects with the ASCE model.
<br>

---

![Representation of the subnetwork within the ASCE model identified by the Forward Influence Blanket that intersects with the Priestley-Taylor model](figs/full-asce-cmb.png)

**Figure 5:** Representation of the subnetwork (blue and black nodes) within the ASCE model identified by the Forward Influence Blanket (blue and green nodes) that intersects with the Priestley-Taylor model.
<br>

---

### Identifying the Forward Influence Blanket (FIB)

Drawing a loose analogy to a [Markov Blanket](https://en.wikipedia.org/wiki/Markov_blanket), a _Forward Influence Blanket_ identifies the variables that are shared between two function networks, along with the non-shared variables that are involved in any functional relationships that are along the directed paths between the shared variables. The FIB gets its name because we are analyzing the _influence_ that variables have on one another in a directed (_forward_ from input to output) network, and the _blanket_ identifies minimal subset of such influences shared between the two networks.

The two figures above depict (through node coloring) the portions of the function networks for the two models identified as overlapping. The nodes in the graphs represent variables, the directed arcs indicate directed functional relationships (the variable at the tail is an input, the variable at the head is the output variable that is a function of the input), and the nodes are color-coded to provide a visual depiction of different relationships with respect to the FIB. 

Consider the second figure, depicting the ASCE function network. All the blue nodes in the network represent variables that are also found in the Priestly-Taylor model. The blue nodes with thicker lines represent variables that play \"input\" roles in both of the overlapping subnetworks: they are shared and do not have any parents that are also in the subnetworks.

Next, between the blue nodes and along the directed paths from the \"inputs\" to the output nodes, are black nodes that represent variables that are not shared between the two models; these indicate intermediate values that may represent differences in the functional relationships between the inputs and outputs of the subnetwork. Determining what the functional differences may be is the subject of the next phase, sensitivity analysis, described in the next section.

In the first figure, depicting the Priestley-Taylor function network, all of the black nodes are between blue nodes. In fact, there are no other nodes or edges that are not colored blue and black. This means the inputs and outputs of the Priestley-Taylor network are \"contained within\" the ASCE network while there are some differences in the computation between the inputs and outputs (the black nodes).

In the ASCE network, however, there are a number of additional nodes: the green colored nodes identify the variables that have directed influence on the computations along the paths from inputs to outputs, although they are _not_ shared between the networks. If one is interested in directly comparing the subnetworks to each other, the states of the green variables may affect the input-to-output relationships.

Finally, the orange nodes represent all of the variables in the ASCE model that are not shared by the Priestley-Taylor model and cannot directly affect the functional relationships between the shared inputs and outputs without either first passing through a blue or green node. It is in this sense that the green and blue nodes together form the **blanket** that isolates the functional relationships between the inputs and outputs that are shared between the two networks. If we understand the functional relationships among the blue and green nodes, then we can separately consider how the orange nodes affect each other, and their relationships are only relevant to describing the behavior of the ASCE model. This provides a nice way of factoring the overall analysis into separate analysis tasks.

Having identified the FIB, with the blue and green nodes constituting all of the inputs that can eventually affect the output(s), we can now turn to analyze the functional relationship between inputs and outputs, including the sensitivity of output variables to input variable values.

### Sensitivity index discovery

In our previous report we demonstrated the ability to automatically
conduct sensitivity analysis on the inputs to an
extracted function network. The method we presented involved three
steps to fully conduct a sensitivity analysis of a given function *f*:

1. Take *N* samples from the input space of *f* using [Saltelli sampling](https://en.wikipedia.org/wiki/Variance-based_sensitivity_analysis)
2. Evaluate each of the *N* samples on *f* to form the set *E*
3. Perform [Sobol analysis](https://en.wikipedia.org/wiki/Variance-based_sensitivity_analysis) on *E*
4. Recover the $$S_1$$, $$S_2$$, and $$S_T$$ sensitivity indices

This method has been successful in retrieving all the information we
needed in order to determine which inputs account for the most
uncertainty in model output. Since our last report the team has begun
investigating how the runtime of sensitivity analysis is affected
by varying the sample size *N* or the size of the input space (number of input variables) of function *f*. The purpose of this study is to understand which aspects of models contribute to the complexity of sensitivity analysis.
Below we present and discuss plots of runtime as a function of
the sample size and number of variables. For each of these graphs the red
line shows the runtime for the entirety of sensitivity analysis and the
blue line shows the runtime of part (3) of the analysis. All run times are in units of seconds.

##### Runtime as a function of sample size

As models become more complex we expect that we will need to
increase the number of samples taken and evaluated in order to achieve
comparable accuracy in sensitivity index estimation during
sensitivity analysis. Because of this, we determined that we needed to
empirically inspect the runtime of sensitivity analysis as the number of
samples increases. From the graph below, we can see that the increase in
runtime as the number of samples increases is nearly linear 
(with slight super-linear trend), both for
the entirety of sensitivity analysis and for the Sobol portion of
sensitivity analysis. This result is encouraging because it suggests that
as long as we maintain only a linear increase in the number of samples
required to conduct sensitivity analysis on our larger models then we
should not see a runtime increase that would render sensitivity analysis
intractable.

<br>

![Plot of the increase in runtime for our Sobol
analysis method as sample size increases. The blue line depicts
the increase in runtime for the Sobol algorithm and the red line depicts
the runtime for the total program.](figs/sa_samples_vs_runtime.png)

**Figure 6:** Plot of the increase in runtime for our Sobol
analysis method as sample size increases. The blue line depicts
the increase in runtime for the Sobol algorithm and the red line depicts
the runtime for the total program.

<br>

##### Runtime as a function of the number of input variables

We are also exploring the impact of increasing the number of input variables considered during an analysis on overall runtime.
As expected, the graph below does show that the runtime for the Sobol portion of sensitivity analysis increases super-linearly as the number of input variables increases. To address this, we are currently exploring several ways to reduce the number of inputs analyzed at one time.
One strategy already described above, motivating the FIB analysis, is to identify modular components of the function network with fewer inputs that can be analyzed independently. We are also exploring doing this at the level of performing sensitivity analysis one function at a time, and then composing the results. This work is ongoing.

<br> 

![Plot of the increase in runtime for the Sobol analysis
method given an increase in number of inputs for the function under
analysis. The blue line depicts the increase in runtime for the Sobol
algorithm and the red line depicts the runtime for the total
program.](figs/sa_inputs_vs_runtime.png)

**Figure 7:** Plot of the increase in runtime for the Sobol
analysis method given an increase in number of inputs for the function
under analysis. The blue line depicts the increase in runtime for the
Sobol algorithm and the red line depicts the runtime for the total
program.

<br>
