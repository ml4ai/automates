## Demo Webapp

### Instructions for running

#### Running the webapp locally

To install Delphi, run the following

```
git clone https://github.com/ml4ai/delphi
cd delphi
pip install .
```

This will also install a command line hook to launch the CodeXplorer app, so
you can just do

```
codex
```

and navigate to [http://127.0.0.1:5000/](http://127.0.0.1:5000/) in your
browser.

#### Accessing the webapp online

CodeXplorer is also live at
[http://vanga.sista.arizona.edu/automates/](http://vanga.sista.arizona.edu/automates/),
where you can try it out without having to install it.

### Updates

The UA team has made numerous improvements to the demo webapp (now christened
CodeXplorer). Below is a screenshot of the current iteration of the app,
showing a computational graph view of the Priestley-Taylor model of potential
evapotranspiration.
![Computational Graph](figs/codex_computational_graph.png)

#### NLP Annotations

Clicking on the variable nodes (maroon ovals) brings up
automatically-associated metadata and provenance for the variables extracted
using NLP from code comments and scientific papers.

![NLP-extracted annotations](figs/codex_annotations.png)

#### Lambda functions and equations

Clicking on the black square nodes brings up the generated Python lambda
function and the equation it represents.

![Lambda functions](figs/codex_lambdas.png)

#### Causal Analysis Graph

Clicking on the "Causal Analysis Graph" tab shows a simplified view of the
model, in which the function nodes are elided, and the edges between the
variable nodes denote causal influence relations. Clicking on the nodes brings
up variable descriptions, similarly to the computational graph view.

![Causal Analysis Graph](figs/codex_cag.png)

#### Sensitivity Surface

The "Sensitivity Surface" tab shows a surface plot of the output variable of
the model with respect to the two input nodes that it is most sensitive to, as
measured by the $$S_2$$ Sobol sensitivity index. Right now, the creation of
this surface depends on knowing the bounds of the variables - right now we use
a hard-coded dictionary of preset bounds for variables in the Priestley-Taylor
model, but in the future we hope to automatically extract domain information
for the variables using machine reading.

![Sensitivity surface](figs/codex_s2_surface.png)

#### Model Comparison

The "Model Comparison" page displays two models of potential evapotranspiration
as implemented in DSSAT - the Priestley-Taylor and ASCE models - and the
'forward influence blanket', i.e. the 'intersection' of the models (shown
below). The blue nodes in the graph indicate variables common to the two
models.

![Model Comparison](figs/codex_model_comparison.png)
