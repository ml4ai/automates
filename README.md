<h1 align="center">Automated Model Assembly<br>from Text, Equations, and Software</h1>

<p align="center">
  <!-- <a href="https://github.com/ml4ai/automates">
   <img src="https://img.shields.io/github/license/ml4ai/automates" />
  </a> -->
  <a href="https://hub.docker.com/r/ml4ailab/automates">
     <img src="https://img.shields.io/docker/cloud/build/ml4ailab/automates" alt="Docker cloud build status">
  </a>
  <a href="https://github.com/ml4ai/automates/actions">
    <img src="https://img.shields.io/github/workflow/status/ml4ai/automates/Continuous%20Integration?label=tests" alt="GH Actions build status">
  </a>
  <a href="https://codecov.io/gh/ml4ai/automates">
   <img src="https://codecov.io/gh/ml4ai/automates/branch/master/graph/badge.svg" />
  </a>
  <a href="https://www.codefactor.io/repository/github/ml4ai/automates"><img src="https://www.codefactor.io/repository/github/ml4ai/automates/badge" alt="CodeFactor" /></a>
</p>

This repository holds the source code for the AutoMATES documentation
and several component pipelines.

For documentation: https://ml4ai.github.io/automates

## Installation instructions
For all operating systems, the first step of the installation process is to clone the AutoMATES repository.

### Linux and macOS
- Create a new [Python virtualenv](https://docs.python.org/3/library/venv.html)
- Activate your new Python virtualenv
- Install Graphviz as defined below
- Run `pip install -e .` from the root of the AutoMATES directory

#### GraphViz installation
##### Debian flavored linux
- Use the command: `sudo apt-get install graphviz libgraphviz-dev pkg-config`
##### macOS with Homebrew
- Use the command: `brew install graphviz`
- Install PyGraphviz to your virtualenv with: `pip install --install-option="--include-path=/usr/local/include/" --install-option="--library-path=/usr/local/lib" pygraphviz`

### Windows
- Download and install [Anaconda](https://www.anaconda.com/products/individual)
- Edit the `PYTHONPATH` variable in `environment.yml` to be your local path to your checkout of the AutoMATES repo
- Run `conda env create --file environment.yml` from the root of the AutoMATES directory
