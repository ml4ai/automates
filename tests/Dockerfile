FROM        ubuntu:19.10
MAINTAINER  Paul D. Hein <pauldhein@email.arizona.edu>
CMD         bash

# ==============================================================================
# INSTALL SOFTWARE VIA THE UBUNTU PACKAGE MANAGER
# ==============================================================================
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update
RUN apt-get -y --no-install-recommends install \
  git \
  curl \
  build-essential \
  gcc \
  pkg-config \
  python3 \
  python3-dev \
  python3-pip \
  openjdk-8-jdk \
  graphviz \
  libgraphviz-dev \
  doxygen

RUN git config --global user.email "pauldhein@email.arizona.edu"
RUN git config --global user.name "Paul Hein"
# ==============================================================================

# ==============================================================================
# INSTALL PYTHON PACKAGES VIA PIP
# NOTE: Packages are installed in stages to avoid memory errors on DockerHub
# ==============================================================================
# Upgrading setuptools and installing wheel
RUN pip3 install --upgrade setuptools
RUN pip3 install wheel

# Common-use and testing packages
RUN pip3 install \
  antlr4-python3-runtime==4.8 \
  pytest==5.4.1 \
  pytest-cov==2.8.1 \
  Pygments==2.3.1 \
  tqdm==4.29.0

# Adding PyTorch separately due to memory constraints
RUN pip3 install \
  torch==1.4.0+cpu \
  -f https://download.pytorch.org/whl/torch_stable.html

# Scientific computing packages
RUN pip3 install \
  networkx==2.4 \
  numpy==1.18.2 \
  pandas==1.0.3 \
  sympy==1.5.1 \
  scikit_learn==0.22.2.post1 \
  SALib==1.3.8 \
  nltk==3.4.5 \
  torchtext==0.5.0

# Python Visualization libraries
RUN pip3 install \
  pygraphviz==1.5 \
  matplotlib==3.2.1 \
  plotly==4.5.4 \
  seaborn==0.10.0

# Web framework packages
RUN pip3 install \
  Flask==1.1.1 \
  flask_codemirror==1.1 \
  flask_wtf==0.14.3 \
  WTForms==2.2.1
# ==============================================================================

# ==============================================================================
# SETUP THE AUTOMATES REPOSITORY AND ENVIRONMENT
# ==============================================================================
RUN git clone https://github.com/ml4ai/automates
ENV PYTHONPATH="/automates/src:$PYTHONPATH"
WORKDIR /automates
# ==============================================================================
