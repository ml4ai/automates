A common method for identifying the probabilistic influences on one or more variables within a probabilistic graphical model is to identify the 
[Markov Blanket](https://en.wikipedia.org/wiki/Markov_blanket) around
a variables. The Markov blanket includes all of the
parent variables of the variables of interest, as well as all the child
variables and parents of child variables. 

For model analysis, we also care about the Markov blanket when we consider how the states of variables may influence our belief about others. However, we seek to first identify the sensitivity variables relationships in deterministic, directed functions, from source inputs to outputs. In this restricted analysis, 

However, for the purposes of model analysis we are currently only interested in
questions pertaining to forward analysis (i.e. how do inputs to the
model affect the output). 

Therefore we have created a loose variant of a
Markov blanket that we have named a Forward Influence Blanket (FIB). Our
rationale for this naming is that a FIB is a _blanket_ around a
probabilistic subnetwork that only captures the information necessary to
determine the _influence_ that nodes have on each other in the _forward_
direction.

The two FIBs shown in the section above are color-coded to provide a
visual depiction of the different components of a FIB. Let us consider
the FIB for the shared subnetwork of the ASCE evapotranspiration model.
We can see that some nodes are colored blue, and of those nodes some are
bolded. All blue nodes in the network represent shared nodes that are
also present in the Priestley-Taylor evapotranspiration model. The blue
nodes that are bolded represent nodes that are shared inputs to both
models (these are likely the nodes of highest interest for model
analysis). Between the blue nodes in our FIB we have a series of one or
more black nodes. These nodes are nodes that are found in the ASCE
factor network but are not present in the Priestley-Taylor factor
network. These nodes likely represent a difference in the computation
used to derive the shared output from the shared inputs in these two
models and they will likely be the cause of differences observed in
model output uncertainty during analysis. We also observe nodes in the
ASCE FIB that are colored green. These nodes are part of the blanket
portion of the FIB that allow us to isolate the probabilistic
subnetworks of the two models. We will need to observe values for these
nodes as well when conducting uncertainty analysis.




### Next steps

##### Sensitivity index propagation

We anticipate that users of AutoMATES will likely want a visual
understanding of how uncertainty is being propagated through our
extracted function networks that represent their models of interest. In
order to accommodate this desire we plan on adapting our sensitivity
index discovery methods to be done on piecewise subnetworks of our
function networks (and FIBs) in a recursive style. This would mean that we
would only consider the immediate parents of a node when running
sensitivity analysis of that particular node. Afterwards we would
conduct sensitivity analysis on each of the parent nodes to determine
the sensitivity indices for each of the parent nodes' parents. Doing this
will allow us to see how sensitivity propagates from the input nodes to
output of any model under study at the finest granularity possible given
our modeling structure.

##### Bayesian sampling for Sensitivity Analysis

Given the results we have presented on in the increase in runtime for
our Sobol algorithm with respect to an increase in sample size and an
increase in the number of inputs, we have decided to investigate
measures to increase the effectiveness of our sampling methods. Although
runtime only increases linearly with an increase in the number of
samples, the amount of samples needed as the number of inputs increases
will increase exponentially due to [the curse of
dimensionality](https://en.wikipedia.org/wiki/Curse_of_dimensionality).
In order to combat this affect and keep our number of necessary samples
to a minimum we are investigating sampling methods via [Bayesian
Optimization](https://en.wikipedia.org/wiki/Bayesian_optimization) that
will allow us to sample our larger search spaces efficiently by taking
into account prior information about the models discovered during text
reading, equation detection, and program analysis.

